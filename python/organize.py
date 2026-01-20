import json
import os
import re
import glob
from collections import defaultdict

# --- FUNÇÕES AUXILIARES ---
def slugify(text):
    if not text: return "unknown"
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')

def extract_manufacturer(casting_name):
    if not casting_name: return "Unknown"
    # (Mantenha sua lista completa de fabricantes aqui - abreviei para economizar espaço)
    real_manufacturers = ["Ferrari", "Lamborghini", "McLaren", "Porsche", "Bugatti", "Ford", "Chevrolet", "Dodge", "Nissan", "Honda", "Toyota", "Mazda"] 
    first_word = casting_name.split()[0]
    if first_word in real_manufacturers: return first_word
    for m in real_manufacturers:
        if m in casting_name: return m
    return "Mattel"

# --- FUNÇÃO PRINCIPAL ---
def organize_batch():
    json_folder = 'json'
    
    # Pega todos os arquivos .json na pasta intermediária
    json_files = glob.glob(os.path.join(json_folder, "*.json"))
    
    if not json_files:
        print(f"❌ Nenhum arquivo JSON encontrado na pasta '{json_folder}/'. Rode o scrapping.py primeiro.")
        return

    print(f"🚀 Iniciando organização de {len(json_files)} arquivos de dados...")

    for json_file in json_files:
        print(f"📂 Lendo: {os.path.basename(json_file)}")
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data_list = json.load(f)
        except Exception as e:
            print(f"   ❌ Erro ao ler arquivo: {e}")
            continue

        for page in data_list:
            # 1. Extração de Dados Básicos
            metadata = page.get('metadata', {})
            casting_name = metadata.get('name', 'Unknown Model')
            casting_id = slugify(casting_name)
            manufacturer = extract_manufacturer(casting_name)
            designer = metadata.get('designer', metadata.get('Designer', 'Unknown'))
            description_text = page.get('description', {}).get('en-us', '')

            # 2. Configurar Diretórios
            casting_dir = 'data/castings'
            os.makedirs(casting_dir, exist_ok=True)
            casting_file = os.path.join(casting_dir, f'{casting_id}.json')

            # 3. Estrutura do Casting
            casting_data = {
                "casting_id": casting_id,
                "name": casting_name,
                "description": {"en-us": description_text, "pt-br": ""},
                "releases": [],
                "specs": {},
                "designer": designer,
                "debut_year": None,
                "manufacturer": manufacturer
            }

            # 4. Processar Releases
            releases_list = page.get('releases', [])
            toy_usage = defaultdict(list)
            
            # Pre-scan para conflitos
            for row in releases_list:
                t_num, yr = row.get('Toy #', '').strip(), row.get('Year', '').strip()
                if t_num and yr: toy_usage[f"{yr}/{t_num}"].append(row)

            for row in releases_list:
                toy_number = row.get('Toy #', '').strip()
                year = row.get('Year', '').strip()
                if not toy_number or not year: continue
                
                # Definição de Caminhos
                key = f"{year}/{toy_number}"
                has_conflict = len(toy_usage[key]) > 1
                filename = f"{toy_number}-{casting_id}.json"
                
                release_dir = f"data/releases/{year}"
                os.makedirs(release_dir, exist_ok=True)
                release_file = os.path.join(release_dir, filename.lower())
                
                # Tratamento de Strings
                base_info = row.get('Base Color/Type', '')
                base_parts = base_info.split(' / ') if ' / ' in base_info else base_info.split('/') if '/' in base_info else [base_info, "Plastic"]
                
                series_raw = row.get('Series', '')
                s_match = re.search(r'(\d+)/(\d+)$', series_raw)
                series_index = int(s_match.group(1)) if s_match else None
                series_name = re.sub(r'\s*\d+/\d+$', '', series_raw).replace('()', '').strip()

                # Objeto Release
                release_data = {
                    "release_id": f"{toy_number.lower()}-{casting_id}-{year}",
                    "toy_number": toy_number,
                    "casting_id": casting_id,
                    "year": int(year),
                    "series_id": slugify(series_name),
                    "series_index": series_index,
                    "specs": {
                        "color": row.get('Color', ''),
                        "tampo": row.get('Tampo', ''),
                        "base_color": base_parts[0].strip(),
                        "base_type": base_parts[1].strip() if len(base_parts) > 1 else "Plastic",
                        "window_color": row.get('Window Color', ''),
                        "interior_color": row.get('Interior Color', ''),
                        "wheel_type": row.get('Wheel Type', '')
                    },
                    "country": row.get('Country', ''),
                    "notes": row.get('Notes', ''),
                    "image_url": row.get('Photo', '')
                }

                # Salvar Release
                with open(release_file, 'w', encoding='utf-8') as f:
                    json.dump(release_data, f, indent=4, ensure_ascii=False)
                
                rel_path = f"data/releases/{year}/{filename.lower()}"
                if rel_path not in casting_data['releases']:
                    casting_data['releases'].append(rel_path)

            # Calcular Debut Year
            if casting_data['releases']:
                years = [int(p.split('/')[2]) for p in casting_data['releases'] if p.split('/')[2].isdigit()]
                if years: casting_data['debut_year'] = min(years)

            # Salvar Casting
            with open(casting_file, 'w', encoding='utf-8') as f:
                json.dump(casting_data, f, indent=4, ensure_ascii=False)

            # 5. Processar Series (Com Merge)
            series_map = defaultdict(list)
            for row in releases_list:
                yr, s_raw = row.get('Year', '').strip(), row.get('Series', '').strip()
                if yr and s_raw:
                    s_name = re.sub(r'\s*\d+/\d+$', '', s_raw).strip()
                    s_id = slugify(s_name)
                    if s_id: series_map[(s_id, yr, s_name)].append(row)

            for (s_id, yr, s_name), rows in series_map.items():
                series_dir = f"data/series/{yr}"
                os.makedirs(series_dir, exist_ok=True)
                series_file = os.path.join(series_dir, f'{s_id}.json')
                
                # Recalcula caminhos dos releases desta série
                new_releases = []
                indices = []
                for row in rows:
                    t_num = row.get('Toy #', '').strip()
                    key = f"{yr}/{t_num}"
                    fname = f"{t_num}-{casting_id}.json" if len(toy_usage[key]) > 1 else f"{t_num}.json"
                    new_releases.append(f"data/releases/{yr}/{fname.lower()}")
                    
                    s_raw = row.get('Series', '')
                    m = re.search(r'(\d+)/(\d+)$', s_raw)
                    if m: indices.append(int(m.group(1)))

                # Carregar existente para MERGE
                final_releases = new_releases
                total_count = len(rows) # Temporário
                
                if os.path.exists(series_file):
                    try:
                        with open(series_file, 'r', encoding='utf-8') as f:
                            existing = json.load(f)
                            # Une as listas sem duplicatas
                            final_releases = list(set(existing.get('releases', []) + new_releases))
                            # Tenta atualizar contagem se possível (aproximado)
                            total_count = max(len(final_releases), existing.get('total_releases', 0))
                    except: pass

                series_data = {
                    "series_id": s_id,
                    "year": int(yr),
                    "name": s_name,
                    "total_releases": total_count, 
                    "max_index": max(indices) if indices else 0,
                    "releases": sorted(final_releases)
                }

                with open(series_file, 'w', encoding='utf-8') as f:
                    json.dump(series_data, f, indent=4, ensure_ascii=False)

            # 6. Processar Brand (Com Merge)
            brand_id = slugify(manufacturer)
            brand_dir = 'data/brands'
            os.makedirs(brand_dir, exist_ok=True)
            brand_file = os.path.join(brand_dir, f'{brand_id}.json')
            
            brand_data = {
                "brand_id": brand_id, "name": manufacturer, "country": "Unknown",
                "founded_year": None, "castings": [], 
                "description": f"Manufacturer of {manufacturer} vehicles."
            }
            
            if os.path.exists(brand_file):
                with open(brand_file, 'r', encoding='utf-8') as f:
                    brand_data = json.load(f)
            
            casting_path = f"data/castings/{casting_id}.json"
            if casting_path not in brand_data['castings']:
                brand_data['castings'].append(casting_path)
            
            with open(brand_file, 'w', encoding='utf-8') as f:
                json.dump(brand_data, f, indent=4, ensure_ascii=False)

    print("\n✅ Organização em lote completa!")

if __name__ == "__main__":
    organize_batch()