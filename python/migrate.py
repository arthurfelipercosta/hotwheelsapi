import os
import json
from collections import defaultdict

def migrate_series():
    series_dir = 'data/series'
    migrated_series = defaultdict(lambda: defaultdict(list))
    
    # Coletar todos os arquivos de séries existentes
    for root, dirs, files in os.walk(series_dir):
        for file in files:
            if file.endswith('.json'):
                year = os.path.basename(root)
                if year.isdigit():  # Só processar pastas de ano
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            series_id = data.get('series_id', file.replace('.json', ''))
                            migrated_series[series_id][year] = data.get('releases', [])
                    except:
                        print(f"Erro ao ler {filepath}")
    
    # Criar novos arquivos consolidados
    for series_id, years_data in migrated_series.items():
        series_file = os.path.join(series_dir, f'{series_id}.json')
        
        # Calcular estatísticas
        total_releases = sum(len(releases) for releases in years_data.values())
        max_index = 0  # Você pode implementar lógica para calcular isso se necessário
        
        # Pegar nome da série do primeiro arquivo encontrado
        series_name = ""
        for year, releases in years_data.items():
            if releases:  # Se há releases neste ano
                # Tentar ler o nome de um arquivo existente neste ano
                year_dir = os.path.join(series_dir, year)
                potential_file = os.path.join(year_dir, f'{series_id}.json')
                if os.path.exists(potential_file):
                    try:
                        with open(potential_file, 'r', encoding='utf-8') as f:
                            existing = json.load(f)
                            series_name = existing.get('name', '')
                            if series_name:
                                break
                    except:
                        pass
        
        # Fallback: converter series_id para nome legível se não conseguiu ler
        if not series_name:
            series_name = series_id.replace('-', ' ').title()
        
        consolidated_data = {
            "series_id": series_id,
            "name": series_name,
            "total_releases": total_releases,
            "max_index": max_index,
            "releases": years_data
        }
        
        with open(series_file, 'w', encoding='utf-8') as f:
            json.dump(consolidated_data, f, indent=4, ensure_ascii=False)
        
        print(f"Migrado: {series_id} ({len(years_data)} anos, {total_releases} releases)")
    
    # Remover pastas de ano vazias (opcional)
    for year in os.listdir(series_dir):
        year_path = os.path.join(series_dir, year)
        if os.path.isdir(year_path) and not os.listdir(year_path):
            os.rmdir(year_path)
            print(f"Removida pasta vazia: {year}")

if __name__ == "__main__":
    migrate_series()
    print("✅ Migração de séries concluída!")