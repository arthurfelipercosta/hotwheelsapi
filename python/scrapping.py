import json
import hashlib
import urllib.parse
import mwparserfromhell
import os
import glob

# --- FUNÇÕES AUXILIARES (Mesmas de antes) ---
def get_wikia_url(filename):
    if not filename: return ""
    clean_name = filename.replace("File:", "").replace("Image:", "").strip()
    clean_name = clean_name.replace(' ', '_')
    md5_hash = hashlib.md5(clean_name.encode('utf-8')).hexdigest()
    h1, h1h2 = md5_hash[0], md5_hash[:2]
    encoded_name = urllib.parse.quote(clean_name)
    return f"https://static.wikia.nocookie.net/hotwheels/images/{h1}/{h1h2}/{encoded_name}"

def clean_text(node):
    if not node: return ""
    return node.strip_code().strip()

def parse_wikitext_robust(content, filename):
    wikicode = mwparserfromhell.parse(content)
    
    # 1. Metadados
    metadata = {}
    templates = wikicode.filter_templates(matches=lambda t: t.name.matches("casting"))
    if templates:
        tmpl = templates[0]
        for param in tmpl.params:
            key = str(param.name).strip()
            value = clean_text(param.value)
            metadata[key] = value
            if key == "image":
                metadata["image_url"] = get_wikia_url(value)

    # 2. Descrição
    description = ""
    sections = wikicode.get_sections(matches="Description")
    if sections:
        desc_node = sections[0]
        for title in desc_node.filter_headings():
            desc_node.remove(title)
        description = clean_text(desc_node)

    # 3. Tabela de Versões
    releases = []
    tables = wikicode.filter_tags(matches=lambda t: t.tag == "table")
    if tables:
        version_table = tables[0]
        for row in version_table.contents.filter_tags(matches=lambda t: t.tag == "tr"):
            cells = row.contents.filter_tags(matches=lambda t: t.tag in ("td", "th"))
            if not cells or len(cells) < 13: continue
            if cells[0].tag == "th": continue

            try:
                img_name = ""
                links = cells[12].contents.filter_wikilinks()
                if links: img_name = str(links[0].title)
                
                release = {
                    "Col #": clean_text(cells[0].contents),
                    "Year": clean_text(cells[1].contents),
                    "Series": clean_text(cells[2].contents),
                    "Color": clean_text(cells[3].contents),
                    "Tampo": clean_text(cells[4].contents),
                    "Base Color/Type": clean_text(cells[5].contents),
                    "Window Color": clean_text(cells[6].contents),
                    "Interior Color": clean_text(cells[7].contents),
                    "Wheel Type": clean_text(cells[8].contents),
                    "Toy #": clean_text(cells[9].contents),
                    "Country": clean_text(cells[10].contents),
                    "Notes": clean_text(cells[11].contents),
                    "Photo": get_wikia_url(img_name)
                }
                releases.append(release)
            except IndexError: continue 

    return {
        "metadata": metadata,
        "description": {"en-us": description, "pt-br": ""},
        "releases": releases,
        "source_file": filename
    }

# --- BLOCO PRINCIPAL (Batch Processing) ---
if __name__ == "__main__":
    txt_folder = "txt"
    json_folder = "json"
    
    # Cria pasta json se não existir
    os.makedirs(json_folder, exist_ok=True)
    
    # Pega todos os .txt
    files = glob.glob(os.path.join(txt_folder, "*.txt"))
    
    print(f"🚀 Iniciando processamento em lote de {len(files)} arquivos...")
    
    for filepath in files:
        filename = os.path.basename(filepath)
        json_filename = filename.replace('.txt', '.json')
        output_path = os.path.join(json_folder, json_filename)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            print(f"⚙️  Processando: {filename}...")
            data = parse_wikitext_robust(content, filename)
            
            # Salvamos como uma lista [data] para manter compatibilidade com o organize.py
            # que espera iterar sobre uma lista de páginas
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump([data], f, indent=4, ensure_ascii=False)
                
            print(f"   ✅ Salvo em: {output_path} ({len(data['releases'])} releases)")
            
        except Exception as e:
            print(f"❌ Erro ao processar {filename}: {e}")

    print("\n🏁 Scraping finalizado! Verifique a pasta 'json/'.")