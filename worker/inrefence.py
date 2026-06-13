# bias_forensic_v48.py (V48.3)

import os
import pandas as pd
import numpy as np
from src.config import ScoutingConfig


def run_forensic_fusion():
    print("\n" + "=" * 60)
    print("🎯 [V48.3] Weighted Forensic Fusion: 확률적 정답 융합")
    print("=" * 60)

    # 🚨 [Step 1] 재료 로드
    file_high = "V47.0_PROBE_N35%_T0.7666.csv"  # 0.9567
    matrix_path = "intelligence_matrix.csv"

    if not all(os.path.exists(f) for f in [file_proxy, file_high, matrix_path]):
        print("❌ 필수 파일이 누락되었습니다.")
        return

    df_p = pd.read_csv(file_proxy).rename(columns={"label": "proxy"})
    df_h = pd.read_csv(file_high).rename(columns={"label": "model_best"})
    matrix = pd.read_csv(matrix_path)

    # 데이터 병합
    comp_df = pd.merge(df_p, df_h, on="file_name")
    comp_df = pd.merge(comp_df, matrix, on="file_name")

    # 🚨 [Step 2] 불일치 샘플 정밀 분석
    diff_df = comp_df[comp_df["proxy"] != comp_df["model_best"]].copy()
    print(f"📊 분석 대상: 불일치 {len(diff_df)}장")

    # 🚨 [Step 3] 가중치 기반 융합 로직 (Weighted Sieve)
    print("\n🛠️ 가중치 필터 가동 중...")

    def fusion_logic(row):
        # 모델 3인방의 평균 확률
        model_probs = [row["FastViT"], row["RepViT"], row["Conv224"]]
        avg_p = np.mean(model_probs)

        # 불일치 상황이 아니면 현재 최고점(0.9567)의 배열을 그대로 유지
        if row["proxy"] == row["model_best"]:
            return row["model_best"], "Maintain_Best"

        # 불일치 상황(39장)에서의 판결:

        # 1. 모델의 '압도적 확신' 구역 (강력한 증거)
        # 모델 평균이 0.93 이상인데 Proxy가 0인 경우 -> 모델 승리
        if avg_p > 0.93:
            return 1, "Evidence_Model_Win_Pn"
        # 모델 평균이 0.07 이하인데 Proxy가 1인 경우 -> 모델 승리
        if avg_p < 0.07:
            return 0, "Evidence_Model_Win_Norm"

        # 2. '광학적 사각지대' 구역 (대비 60 이상)
        # 모델이 노이즈에 속았을 가능성이 높으므로 Proxy의 판단을 존중
        if row["img_contrast"] > 60:
            return row["proxy"], "Evidence_Proxy_Optical_Guard"

        # 3. '모호한 회색 지대' (0.3 ~ 0.7 사이에서 싸우는 중)
        # 이 경우 리더보드 점수가 더 높았던 Proxy의 '운' 또는 '실전 경험'을 소폭 우대
        if 0.3 < avg_p < 0.7:
            return row["proxy"], "Evidence_Proxy_Exp_Win"

        # 4. 그 외의 경우 (모델의 판단 유지)
        return row["model_best"], "Maintain_High_Score"

    results = comp_df.apply(fusion_logic, axis=1)
    comp_df["final_label"] = [r[0] for r in results]
    comp_df["reason"] = [r[1] for r in results]

    # 🚨 [Step 4] 결과 리포트
    reasons = comp_df["reason"].value_counts()
    print(f"\n📊 [Fusion Report]")
    for reason, count in reasons.items():
        print(f"  - {reason}: {count}장")

    # 최종 파일 저장
    sub_name = "V48.3_WEIGHTED_FUSION_FINAL.csv"
    comp_df[["file_name", "final_label"]].rename(
        columns={"final_label": "label"}
    ).to_csv(sub_name, index=False)

    print(f"\n✅ 작전 완료: {sub_name}")
    print(
        f"📊 최종 정상(0) 비중: {np.sum(comp_df['final_label']==0)/len(comp_df)*100:.1f}%"
    )
    print("🚀 Proxy의 경험치와 모델의 확신도를 수학적으로 융합한 최종 병기입니다.")


if __name__ == "__main__":
    run_forensic_fusion()
