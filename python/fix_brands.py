import os
import json
import re

def slugify(text):
    """Converte texto para slug URL-friendly"""
    if not text: return "unknown"
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')

car_to_manufacturer = {
    r"\bCorvette\b": "Chevrolet",
    r"\bChevelle\b": "Chevrolet",
    r"\bChevy\b": "Chevrolet",
    r"\bMustang\b": "Ford", 
    r"\bCamaro\b": "Chevrolet",
    r"\bChallenger\b": "Dodge",
    r"\bCharger\b": "Dodge",
    r"\bImpala\b": "Chevrolet",
    r"\bViper\b": "Dodge",
    r"\bLancer\b": "Mitsubishi",
    r"\bEscort\b":"Ford",
    r"\bRam\b": "Dodge"
}

def extract_manufacturer(casting_name):
    """Extrai fabricante do nome do casting (mesma lógica do organize.py)"""
    if not casting_name: return "Unknown"

    for pattern, manufacturer in car_to_manufacturer.items():
        if re.search(pattern, casting_name, re.IGNORECASE):
            return manufacturer
    
    real_manufacturers = [
        "Acura", "Alfa Romeo", "Aston Martin", "Audi", "Bentley", "BMW", "Bugatti", "Buick", "Cadillac", "Citroen", "Chevrolet", "Chevy", "Datsun", "Dodge", "Ducati", "Ferrari", "Fiat", "Ford", "GMC", "Honda", "Jaguar", "Jeep", "Kia", "Koenigsegg", "Lamborghini", "Lancia", "Land Rover", "Lincoln", "Lotus", "Maserati", "Mercedes", "Mercury", "Mazda", "McLaren", "Mini", "Mitsubishi", "Nissan", "Pagani", "Peugeot", "Plymouth", "Pontiac", "Porsche", "Range Rover", "Renault", "Rimac", "Shelby", "Subaru", "Tesla", "Toyota", "Volvo", "Volkswagen"
    ]
    
    first_word = casting_name.split()[0]
    for manufacturer in real_manufacturers:
        if manufacturer.lower() == first_word.lower():
            return manufacturer
    
    for m in real_manufacturers:
        if m.lower() in casting_name.lower(): 
            return m
    
    return "Mattel"

def fix_brand_castings():
    """Verifica e corrige castings nas marcas erradas"""
    
    brands_dir = 'data/brands'
    castings_moved = []
    
    print("🔍 Verificando arquivos de marcas...")
    
    # Carregar todos os arquivos de marca
    brand_files = {}
    for filename in os.listdir(brands_dir):
        if filename.endswith('.json'):
            brand_name = filename[:-5]  # remove .json
            filepath = os.path.join(brands_dir, filename)
            
            with open(filepath, 'r', encoding='utf-8') as f:
                brand_files[brand_name] = json.load(f)
    
    print(f"📂 Carregados {len(brand_files)} arquivos de marca")
    
    # FAZER UMA CÓPIA PARA ITERAR (evita erro de modificação durante iteração)
    brand_files_copy = brand_files.copy()
    
    # Verificar cada casting em cada marca
    for brand_name, brand_data in brand_files_copy.items():  # <-- USAR A CÓPIA AQUI
        castings_to_remove = []
        
        for casting_path in brand_data.get('castings', []):
            # Extrair nome do casting do path
            casting_filename = casting_path.split('/')[-1]  # "17-audi-rs6-avant.json"
            casting_name = casting_filename[:-5]  # "17-audi-rs6-avant"
            
            # Converter para nome legível (remover números do início se houver)
            readable_name = re.sub(r'^\d+-', '', casting_name).replace('-', ' ')
            readable_name = ' '.join(word.capitalize() for word in readable_name.split())
            
            # Extrair fabricante correto
            correct_manufacturer = extract_manufacturer(readable_name)
            correct_brand_slug = slugify(correct_manufacturer)
            
            if correct_brand_slug != brand_name:
                print(f"❌ {casting_filename} está em {brand_name}.json mas deveria estar em {correct_brand_slug}.json")
                
                # Adicionar à marca correta (agora pode modificar brand_files sem erro)
                if correct_brand_slug not in brand_files:
                    # Criar nova marca se não existir
                    brand_files[correct_brand_slug] = {
                        "brand_id": correct_brand_slug,
                        "name": correct_manufacturer,
                        "country": "Unknown",
                        "founded_year": None,
                        "castings": [],
                        "description": {
                            "en-us": f"Manufacturer of {correct_manufacturer} vehicles.",
                            "pt-br": f"Fabricante de veículos {correct_manufacturer}."
                        }
                    }
                    print(f"✨ Criada nova marca: {correct_brand_slug}.json")
                
                if casting_path not in brand_files[correct_brand_slug]['castings']:
                    brand_files[correct_brand_slug]['castings'].append(casting_path)
                    castings_moved.append(f"{casting_filename}: {brand_name} → {correct_brand_slug}")
                
                # Marcar para remoção da marca errada
                castings_to_remove.append(casting_path)
        
        # Remover castings da marca errada
        for casting_path in castings_to_remove:
            brand_data['castings'].remove(casting_path)
    
    # Salvar todos os arquivos atualizados
    print("\n💾 Salvando arquivos atualizados...")
    for brand_name, brand_data in brand_files.items():
        # Ordenar castings para manter consistência
        brand_data['castings'].sort()
        
        filepath = os.path.join(brands_dir, f'{brand_name}.json')
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(brand_data, f, indent=4, ensure_ascii=False)
    
    print(f"\n✅ Correção completa! {len(castings_moved)} castings movidos:")
    for move in castings_moved:
        print(f"   🔄 {move}")
    
    if not castings_moved:
        print("   🎉 Nenhum casting estava no lugar errado!")

if __name__ == "__main__":
    fix_brand_castings()