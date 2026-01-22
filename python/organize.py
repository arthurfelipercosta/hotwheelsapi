import sys
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
    real_manufacturers = ["Acura", "Alfa Romeo", "Aston Martin", "Audi", "Bentley", "BMW", "Bugatti", "Buick", "Cadillac", "Citroen", "Chevrolet", "Chevy", "Datsun", "Dodge", "Ducati", "Ferrari", "Fiat", "Ford", "GMC", "Honda", "Jaguar", "Jeep", "Kia", "Koenigsegg", "Lamborghini", "Lancia", "Land Rover", "Lincoln", "Lotus", "Maserati", "Mercedes", "Mercury", "Mazda", "McLaren", "Mini", "Mitsubishi", "Nissan", "Pagani", "Peugeot", "Plymouth", "Pontiac", "Porsche", "Range Rover", "Renault", "Rimac", "Shelby", "Subaru", "Tesla", "Toyota", "Volvo", "Volkswagen"] 
    first_word = casting_name.split()[0]
    if first_word in real_manufacturers: return first_word
    for m in real_manufacturers:
        if m in casting_name: return m
    return "Mattel"

# --- FUNÇÃO PRINCIPAL ---
def organize_batch(json_folder='json'):
    # Rastreia arquivos criados NESTA execução para evitar duplicatas infinitas (v2, v3...)
    generated_files_registry = set()

    # Busca recursiva em subpastas
    # json_files = glob.glob(os.path.join(json_folder, "**/*.json"), recursive=True) # TODAS
    json_files = glob.glob(os.path.join(json_folder, "*.json")) # SÓ UMA PASTA
    
    if not json_files:
        print(f"❌ Nenhum arquivo JSON encontrado em '{json_folder}/'.")
        return

    print(f"🚀 Iniciando organização de {len(json_files)} arquivos...")

    for json_file in json_files:
        print(f"📂 Lendo: {os.path.basename(json_file)}")
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data_list = json.load(f)
        except Exception as e:
            print(f"   ❌ Erro ao ler arquivo: {e}")
            continue

        for page in data_list:
            # 1. Extração
            metadata = page.get('metadata', {})
            casting_name = metadata.get('name', 'Unknown Model')
            casting_id = slugify(casting_name)
            manufacturer = extract_manufacturer(casting_name)
            designer = metadata.get('designer', metadata.get('Designer', 'Unknown'))
            description_text = page.get('description', {}).get('en-us', '')

            # 2. Configurar Diretórios e Casting
            casting_dir = 'data/castings'
            os.makedirs(casting_dir, exist_ok=True)
            casting_file = os.path.join(casting_dir, f'{casting_id}.json')

            casting_data = {
                "casting_id": casting_id,
                "name": casting_name,
                "description": {
                    "en-us": description_text,
                    "pt-br": ""
                },
                "releases": [],
                "specs": {},
                "designer": designer,
                "debut_year": None,
                "manufacturer": manufacturer
            }

            # 3. Processar Releases
            releases_list = page.get('releases', [])
            
            for row in releases_list:
                toy_number = row.get('Toy #', '').strip()
                raw_year = row.get('Year', '').strip()
                years = re.findall(r'\b(?:19|20)\d{2}\b', raw_year)
                if not toy_number or not years: continue
                year = years[0]
                
                # Tratamento de Strings
                base_info = row.get('Base Color / Type', '')
                base_parts = base_info.split(' / ') if ' / ' in base_info else base_info.split('/') if '/' in base_info else [base_info, "Plastic"]
                
                series_raw = row.get('Series', '')
                s_match = re.search(r'(\d+)/(\d+)$', series_raw)
                series_index = int(s_match.group(1)) if s_match else None
                series_name = re.sub(r'\s*\d+/\d+$', '', series_raw).replace('()', '').strip()

                # --- LÓGICA DE NOMEAÇÃO IDEMPOTENTE ---
                release_dir = f"data/releases/{year}"
                os.makedirs(release_dir, exist_ok=True)

                clean_toy_num = slugify(toy_number) 
                base_filename = f"{clean_toy_num}-{casting_id}"
                
                filename = f"{base_filename}.json"
                file_path = os.path.join(release_dir, filename)
                
                # Verifica conflito na MEMÓRIA da execução atual, não no disco
                counter = 2
                while file_path in generated_files_registry:
                    filename = f"{base_filename}-v{counter}.json"
                    file_path = os.path.join(release_dir, filename)
                    counter += 1
                
                # Registra que este arquivo já foi "tomado" nesta rodada
                generated_files_registry.add(file_path)

                # --- Sempre normalizado ---
                raw_wheel = row.get('Wheel Type', '').strip()
                raw_images = row.get('Photo', '').strip()

                # separadores possíveis no fandom
                parts = re.split(r'\s*/\s*|\s*,\s*|\s+and\s+', raw_wheel)

                images = {"0": raw_images} if raw_images else {}

                if len(parts) > 1:
                    wheel_type = {
                        str(i): part.strip()
                        for i, part in enumerate(parts)
                        if part.strip()
                    }
                else:
                    wheel_type = {"0": raw_wheel} if raw_wheel else {}
                # Objeto Release
                release_data = {
                    "release_id": f"{clean_toy_num}-{casting_id}-{year}",
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
                        "wheel_type": wheel_type
                    },
                    "country": row.get('Country', ''),
                    "notes": row.get('Notes', ''),
                    "images": images
                }

                # Salva (sobrescreve se já existir no disco)
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(release_data, f, indent=4, ensure_ascii=False)
                
                rel_path = f"data/releases/{year}/{filename.lower()}"
                if rel_path not in casting_data['releases']:
                    casting_data['releases'].append(rel_path)

            # 4. Finalizar Casting
            if casting_data['releases']:
                years = []
                for p in casting_data['releases']:
                    try: years.append(int(p.split('/')[2]))
                    except: pass
                if years: casting_data['debut_year'] = min(years)

            with open(casting_file, 'w', encoding='utf-8') as f:
                json.dump(casting_data, f, indent=4, ensure_ascii=False)

            # 5. Processar Series
            series_map = defaultdict(lambda: defaultdict(list))
            for row in releases_list:
                raw_yr = row.get('Year', '').strip()
                s_raw = row.get('Series', '').strip()
                years = re.findall(r'\b(?:19|20)\d{2}\b', raw_yr)
                if not years or not s_raw: continue
                yr = years[0]
                s_name = re.sub(r'\s*\d+/\d+$', '', s_raw).strip()
                s_id = slugify(s_name)
                if s_id: series_map[s_id][yr].append(row)

            for s_id, years_data in series_map.items():
                series_dir = 'data/series'  # Pasta raiz das séries (não por ano)
                os.makedirs(series_dir, exist_ok=True)
                series_file = os.path.join(series_dir, f'{s_id}.json')
                
                # Carregar dados existentes se o arquivo já existir
                existing_data = {}
                if os.path.exists(series_file):
                    try:
                        with open(series_file, 'r', encoding='utf-8') as f:
                            existing_data = json.load(f)
                    except: pass
                
                # Consolidar dados de todos os anos
                all_releases = {}
                total_count = 0
                max_index = 0
                series_name = ""
                
                for yr, rows in years_data.items():
                    yr_str = str(yr)
                    
                    # Recalcula caminhos para este ano
                    new_releases = []
                    indices = []
                    for row in rows:
                        t_num = row.get('Toy #', '').strip()
                        clean_t_num = slugify(t_num)
                        fname = f"{clean_t_num}-{casting_id}.json"
                        new_releases.append(f"data/releases/{yr}/{fname.lower()}")
                        
                        s_raw = row.get('Series', '')
                        m = re.search(r'(\d+)/(\d+)$', s_raw)
                        if m: indices.append(int(m.group(1)))
                    
                    # Combinar com dados existentes para este ano
                    existing_year_releases = existing_data.get('releases', {}).get(yr_str, [])
                    combined = existing_year_releases + [x for x in new_releases if x not in existing_year_releases]
                    all_releases[yr_str] = sorted(combined)
                    
                    total_count += len(combined)
                    if indices:
                        max_index = max(max_index, max(indices))
                    
                    # Pegar o nome da série do primeiro row válido
                    if not series_name and rows:
                        series_name = re.sub(r'\s*\d+/\d+$', '', rows[0].get('Series', '')).strip()
                
                # Usar nome existente se disponível
                if existing_data.get('name'):
                    series_name = existing_data['name']
                
                series_data = {
                    "series_id": s_id,
                    "name": series_name,
                    "total_releases": max(total_count, existing_data.get('total_releases', 0)),
                    "max_index": max(max_index, existing_data.get('max_index', 0)),
                    "releases": all_releases
                }

                with open(series_file, 'w', encoding='utf-8') as f:
                    json.dump(series_data, f, indent=4, ensure_ascii=False)

    print("\n✅ Organização em lote completa!")

if __name__ == "__main__":
    json_folder = sys.argv[1] if len(sys.argv) > 1 else 'json'
    organize_batch(json_folder)