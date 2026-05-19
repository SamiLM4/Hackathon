import pandas as pd
import numpy as np
from pathlib import Path

def align_and_clean_datasets():
    base_dir = Path(__file__).resolve().parent.parent
    processed_dir = base_dir / 'data' / 'processed'
    
    print("=== ALINHAMENTO DE COLUNAS (Fase 4/7) ===")
    
    # 1. Carregar arquivos originais
    train_path = processed_dir / 'X_train_baseline.csv'
    val_path = processed_dir / 'X_val_baseline.csv'
    hold_path = processed_dir / 'X_hold_baseline.csv'
    train_comp_path = processed_dir / 'X_treino_baseline_completo.csv'
    sub_path = processed_dir / 'df_sub_ordenada.csv'
    
    if not all(p.exists() for p in [train_path, val_path, hold_path, train_comp_path, sub_path]):
        # Backup check for other file names
        if (processed_dir / 'X_sub_baseline.csv').exists():
            sub_path = processed_dir / 'X_sub_baseline.csv'
            print(f"Usando X_sub_baseline.csv como submissao.")
        else:
            print("❌ Erro: Alguns arquivos base não foram encontrados em data/processed/")
            return
            
    print("Lendo bases...")
    df_train = pd.read_csv(train_path)
    df_val = pd.read_csv(val_path)
    df_hold = pd.read_csv(hold_path)
    df_train_comp = pd.read_csv(train_comp_path)
    df_sub = pd.read_csv(sub_path)
    
    print(f"Colunas originais no Treino           : {len(df_train.columns)}")
    print(f"Colunas originais no Treino Completo  : {len(df_train_comp.columns)}")
    print(f"Colunas originais na Validação         : {len(df_val.columns)}")
    print(f"Colunas originais na Submissão         : {len(df_sub.columns)}")
    
    # Identificar colunas alvo e identificadores
    target_col = 'FPD'
    id_col = 'pedido_id'
    
    # 2. Corrigir os bugs de codificação (Label Encoding dinâmico)
    # score_encoded, idade_encoded, order_bump_encoded não devem ser tratados como texto e encoded.
    # Vamos dropar as versões _encoded dessas colunas se existirem
    cols_to_drop = ['score_encoded', 'idade_encoded', 'order_bump_encoded']
    for df in [df_train, df_val, df_hold, df_train_comp, df_sub]:
        df.drop(columns=[c for c in cols_to_drop if c in df.columns], errors='ignore', inplace=True)
        
    # 3. Mapeamento e Alinhamento do Bureau Versão 5
    # Na submissão, alguns scores vieram com prefixo "SCORE_" ou versões diferentes.
    # Vamos fazer o rename na submissão se as colunas equivalentes existirem:
    renames = {
        'SCORE_HPG5': 'HPG5',
        'SCORE_H5OR': 'H5OR',
        'HI02_PROB': 'HI01_PROB',
        'HI02_CONCEITO': 'HI01_CONCEITO',
        'SCORE_HCR4': 'HCR5', # Versão aproximada (V4 para V5) para não perder a feature
    }
    df_sub.rename(columns=renames, inplace=True)
    
    # 4. Encontrar as colunas que estão no Treino mas não estão na Submissão
    # E vice-versa
    train_features = [c for c in df_train.columns if c not in [target_col]]
    sub_features = [c for c in df_sub.columns]
    
    missing_in_sub = [c for c in train_features if c not in sub_features]
    missing_in_train = [c for c in sub_features if c not in train_features]
    
    print("\n[!] Mapeamento de divergencias:")
    print(f"  - No Treino mas nao na Submissao ({len(missing_in_sub)}): {missing_in_sub}")
    print(f"  - Na Submissao mas nao no Treino ({len(missing_in_train)}): {missing_in_train}")
    
    # 5. Para garantir alinhamento perfeito, vamos manter apenas a intersecao das colunas preditoras
    common_features = [c for c in train_features if c in sub_features]
    
    # Manter ID no index ou nas colunas
    final_features_train = common_features + [target_col]
    final_features_sub = common_features
    
    df_train_aligned = df_train[final_features_train].copy()
    df_val_aligned = df_val[final_features_train].copy()
    df_hold_aligned = df_hold[final_features_train].copy()
    df_train_comp_aligned = df_train_comp[final_features_train].copy()
    df_sub_aligned = df_sub[final_features_sub].copy()
    
    # 6. Salvar arquivos alinhados
    df_train_aligned.to_csv(processed_dir / 'X_train_aligned.csv', index=False)
    df_val_aligned.to_csv(processed_dir / 'X_val_aligned.csv', index=False)
    df_hold_aligned.to_csv(processed_dir / 'X_hold_aligned.csv', index=False)
    df_train_comp_aligned.to_csv(processed_dir / 'X_train_completo_aligned.csv', index=False)
    df_sub_aligned.to_csv(processed_dir / 'X_sub_aligned.csv', index=False)
    
    print(f"\n[OK] Alinhamento concluido com sucesso!")
    print(f"  - Colunas finais preditoras: {len(common_features)}")
    print(f"  - Arquivos salvos em: {processed_dir.resolve()}")
    print(f"    - X_train_aligned.csv ({len(df_train_aligned)} linhas)")
    print(f"    - X_val_aligned.csv ({len(df_val_aligned)} linhas)")
    print(f"    - X_hold_aligned.csv ({len(df_hold_aligned)} linhas)")
    print(f"    - X_train_completo_aligned.csv ({len(df_train_comp_aligned)} linhas)")
    print(f"    - X_sub_aligned.csv ({len(df_sub_aligned)} linhas)")

if __name__ == '__main__':
    align_and_clean_datasets()
