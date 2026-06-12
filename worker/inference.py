import os
import torch
import torch.nn as nn
import torchvision.transforms as transforms
from PIL import Image
import timm
from typing import Tuple, List

# 지원 모델 카탈로그 매핑 (timm 백본 이름 및 학습 해상도)
MODEL_CATALOG = {
    "ConvNeXt-Tiny-Surgical": {"name": "convnext_tiny", "resolution": 224},
    "FastViT-SA12": {"name": "fastvit_sa12", "resolution": 224},
    "RepViT-M1.1": {"name": "repvit_m1_1", "resolution": 224}
}

# ImageNet 표준 정규화 파라미터
NORMALIZE = transforms.Normalize(
    mean=[0.485, 0.456, 0.406],
    std=[0.229, 0.224, 0.225]
)

def get_inference_transforms(resolution: int = 224):
    """
    _x_ray_codes/data_loader.py의 검증 파이프라인과 동일한 전처리 적용:
    Resize(280) -> CenterCrop(224) -> ToTensor() -> Normalize()
    """
    crop_ratio = 0.8
    scaled_res = int(resolution / crop_ratio)  # 224 / 0.8 = 280
    
    return transforms.Compose([
        transforms.Resize(scaled_res, interpolation=transforms.InterpolationMode.BICUBIC),
        transforms.CenterCrop(resolution),
        transforms.ToTensor(),
        NORMALIZE
    ])

class EnsembleInference:
    def __init__(self, model_key: str, models_dir: str = "worker/models"):
        if model_key not in MODEL_CATALOG:
            raise ValueError(f"지원하지 않는 모델 키입니다: {model_key}")
            
        self.model_key = model_key
        self.model_info = MODEL_CATALOG[model_key]
        self.resolution = self.model_info["resolution"]
        self.transform = get_inference_transforms(self.resolution)
        self.device = torch.device("cpu")  # CPU에서 안전하게 구동
        
        # 해당 모델의 5개 Fold 가중치 경로 리스트 빌드
        self.weight_paths = []
        for fold in range(1, 6):
            weight_path = os.path.join(models_dir, f"{model_key}_Fold{fold}.pth")
            if os.path.exists(weight_path):
                self.weight_paths.append(weight_path)
        
        if not self.weight_paths:
            raise FileNotFoundError(f"❌ {model_key}에 매칭되는 .pth 가중치 파일들을 {models_dir}에서 찾을 수 없습니다.")
            
        print(f"✅ {model_key} 앙상블 모델 초기화 완료 (발견된 Folds: {len(self.weight_paths)}개)")
        
        # 모델 뼈대 사전 로드 (지연 인스턴스화를 방지하기 위해 생성자에서 가중치까지 미리 올려둠)
        self.models = []
        for path in self.weight_paths:
            try:
                # 3채널 RGB 규격으로 백본 빌드 (num_classes=2)
                model = timm.create_model(self.model_info["name"], pretrained=False, num_classes=2)
                state_dict = torch.load(path, map_location=self.device)
                model.load_state_dict(state_dict)
                model.to(self.device)
                model.eval()
                self.models.append(model)
            except Exception as e:
                print(f"⚠️ 가중치 로드 실패 ({os.path.basename(path)}): {e}")

    def predict(self, image_path: str) -> Tuple[bool, float]:
        """
        이미지를 전처리하고 각 Fold 모델의 예측 확률값을 평균하여 최종 진단 및 신뢰도 도출
        """
        if not self.models:
            raise RuntimeError("로드 완료된 모델 가중치가 없습니다.")

        # 1. 이미지 로드 및 RGB 3채널 변환
        image = Image.open(image_path).convert("RGB")
        input_tensor = self.transform(image).unsqueeze(0).to(self.device)  # [1, 3, 224, 224]

        # 2. 모든 Fold 모델의 예측 결과(Softmax 확률값) 누적
        total_probs = torch.zeros(1, 2).to(self.device)
        with torch.no_grad():
            for model in self.models:
                outputs = model(input_tensor)
                probs = torch.softmax(outputs, dim=1)
                total_probs += probs

        # 3. 평균 확률 계산
        avg_probs = total_probs / len(self.models)
        
        # Class 0: Normal, Class 1: Pneumonia
        normal_prob = avg_probs[0, 0].item()
        pneumonia_prob = avg_probs[0, 1].item()
        
        is_pneumonia = pneumonia_prob >= 0.5
        confidence = pneumonia_prob if is_pneumonia else normal_prob
        confidence_percent = round(confidence * 100, 1)

        return is_pneumonia, confidence_percent

_LOADED_ENGINES = {}

def run_prediction(image_path: str, model_key: str = "FastViT-SA12") -> Tuple[bool, float, str]:
    """
    외부에서 간편하게 호출할 수 있는 단일 예측 엔트리포인트 함수
    """
    global _LOADED_ENGINES
    if model_key not in _LOADED_ENGINES:
        _LOADED_ENGINES[model_key] = EnsembleInference(model_key=model_key)
    
    engine = _LOADED_ENGINES[model_key]
    is_pneumonia, confidence = engine.predict(image_path)
    return is_pneumonia, confidence, model_key
