import requests
from bs4 import BeautifulSoup
import json
import hashlib
import urllib.parse

def get_wikia_url(filename):
    """Gera a URL oficial da Wikia baseada no nome do arquivo"""
    if not filename: return ""
    filename = filename.strip().replace(' ', '_')
    md5_hash = hashlib.md5(filename.encode('utf-8')).hexdigest()
    h1, h1h2 = md5_hash[0], md5_hash[:2]
    encoded_name = urllib.parse.quote(filename)
    return f"https://static.wikia.nocookie.net/hotwheels/images/{h1}/{h1h2}/{encoded_name}"

# LISTA DE LINKS
urls = [
    "https://hotwheels.fandom.com/wiki/Bugatti_Veyron_(2023)"
]

def scrape_everything(url):
    print(f"Reading: {url}")
    try:
        # Headers para simular navegador e evitar erro 403
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
        }
        
        response = requests.get(url, headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Erro: Status {response.status_code}")
            return None
            
        soup = BeautifulSoup(response.text, 'html.parser')

        # EXTRAÇÃO DE METADADOS (Designer, etc)
        metadata = {}
        infobox = soup.find('aside', class_='portable-infobox')
        if infobox:
            for item in infobox.find_all('div', class_='pi-item'):
                label = item.find(['h3', 'div'], class_='pi-data-label')
                value = item.find(['div'], class_='pi-data-value')
                if label and value:
                    key = label.get_text(strip=True).replace(':', '')
                    val = value.get_text(strip=True)
                    metadata[key] = val

        page_data = {
            "url": url,
            "title": soup.find('h1').get_text(strip=True) if soup.find('h1') else "Sem Título",
            "metadata": metadata,
            "tables": [],
            "paragraphs": [p.get_text(strip=True) for p in soup.find_all('p') if p.get_text(strip=True)]
        }

        # PEGAR AS TABELAS
        for table in soup.find_all('table', class_='wikitable'):
            rows = []
            tr_list = table.find_all('tr')
            if not tr_list: continue
            
            headers = [th.get_text(strip=True) for th in tr_list[0].find_all(['th', 'td'])]
            
            for tr in tr_list[1:]:
                cells = tr.find_all(['td', 'th'])
                row_dict = {}
                for i, cell in enumerate(cells):
                    header = headers[i] if i < len(headers) else f"col_{i}"
                    
                    # Se for a coluna de Foto, busca a tag img
                    if header == "Photo":
                        img_tag = cell.find('img')
                        if img_tag:
                            img_name = img_tag.get('data-image-name') or img_tag.get('alt')
                            row_dict[header] = get_wikia_url(img_name)
                        else:
                            row_dict[header] = ""
                    else:
                        # Para as outras colunas, mantém a lógica do <br> e texto
                        for br in cell.find_all("br"):
                            br.replace_with(" ")
                        row_dict[header] = cell.get_text(" ", strip=True)
                if row_dict:
                    rows.append(row_dict)
            page_data["tables"].append(rows)

        return page_data
    except Exception as e:
        print(f"Erro ao processar {url}: {e}")
        return None

if __name__ == "__main__":
    all_results = []
    for url in urls:
        res = scrape_everything(url)
        if res:
            all_results.append(res)
        else:
            print(f"❌ Falhou para: {url}")

    if all_results:
        with open('scrapping.json', 'w', encoding='utf-8') as f:
            json.dump(all_results, f, indent=4, ensure_ascii=False)
        
        print(f"\n✅ Concluído! {len(all_results)} links salvos em 'scrapping.json'")
    else:
        print("\n❌ Nenhum link foi processado com sucesso.")