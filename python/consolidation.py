import os
import json
from collections import defaultdict

def consolidation():
    series_dir = 'data/series'
    
    # Mapeamento de séries principais e suas sub-séries
    hierarchical_consolidations = {
        'pop-culture': {
            'sub_series': ['pop-culture-alex-ross-dc-heroes', 'pop-culture-archie-comics', 'pop-culture-archie', 'pop-culture-back-to-the-future', 'pop-culture-barbie', 'pop-culture-batman-classic-tv-series', 'pop-culture-batman-forever', 'pop-culture-batman-the-animated-series', 'pop-culture-batman', 'pop-culture-dc-comics-batman-superman', 'pop-culture-dc-comics', 'pop-culture-disney', 'pop-culture-forza', 'pop-culture-general-mills', 'pop-culture-gran-turismo', 'pop-culture-grateful-dead', 'pop-culture-hanna-barbera', 'pop-culture-jay-leno-s-garage', 'pop-culture-just-born', 'pop-culture-king-features-syndicate', 'pop-culture-knight-rider', 'pop-culture-led-zeppelin', 'pop-culture-looney-tunes', 'pop-culture-m-m-mars', 'pop-culture-mad-magazine', 'pop-culture-mars', 'pop-culture-marvel-studios-concept-art', 'pop-culture-marvel', 'pop-culture-masters-of-the-universe', 'pop-culture-mattel-80th-anniversary', 'pop-culture-mattel-brands', 'pop-culture-mtv', 'pop-culture-nestle', 'pop-culture-peanuts', 'pop-culture-rick-and-morty', 'pop-culture-scooby-doo', 'pop-culture-speed-shop-garage', 'pop-culture-speed-shop', 'pop-culture-spongebob-squarepants', 'pop-culture-star-trek-50th-anniversary', 'pop-culture-star-trek', 'pop-culture-star-wars-bounty-hunter', 'pop-culture-star-wars', 'pop-culture-street-fighter-v', 'pop-culture-super-mario-bros', 'pop-culture-teenage-mutant-ninja-turtles', 'pop-culture-the-beatles', 'pop-culture-the-dark-knight-trilogy', 'pop-culture-the-mandalorian-concept-art', 'pop-culture-the-matrix', 'pop-culture-the-muppets', 'pop-culture-top-gun-maverick', 'pop-culture-vintage-oil', 'pop-culture-women-of-marvel', 'pop-culture-x-men', 'pop-culture-yellow-submarine'],
            'name': 'Pop Culture'
        },
        'car-culture': {
            'sub-series': ['car-culture-air-cooled', 'car-culture-american-scene', 'car-culture-british-horsepower', 'car-culture-canyon-warriors', 'car-culture-cargo-carriers', 'car-culture-cars-donuts', 'car-culture-circuit-legends', 'car-culture-cruise-boulevard', 'car-culture-desert-rally', 'car-culture-door-slammers', 'car-culture-dragstrip-demons', 'car-culture-euro-style', 'car-culture-eurospeed', 'car-culture-exotic-envy', 'car-culture-fast-wagons', 'car-culture-gulf', 'car-culture-hammer-drop', 'car-culture-hw-off-road', 'car-culture-hw-redliners', 'car-culture-hyper-haulers', 'car-culture-japan-historics-2', 'car-culture-japan-historics-3', 'car-culture-japan-historics-4', 'car-culture-japan-historics-5', 'car-culture-japan-historics', 'car-culture-jay-leno-s-garage', 'car-culture-knight-rider-2-pack', 'car-culture-modern-classics', 'car-culture-mountain-drifters', 'car-culture-open-track', 'car-culture-power-trip', 'car-culture-premium-boxed-set', 'car-culture-race-day', 'car-culture-ronin-run', 'car-culture-shop-trucks', 'car-culture-silhouettes', 'car-culture-slide-street-2', 'car-culture-slide-street', 'car-culture-speed-machines', 'car-culture-street-tuners', 'car-culture-team-transport-8', 'car-culture-team-transport-9', 'car-culture-team-transport-13', 'car-culture-team-transport-16', 'car-culture-team-transport-18', 'car-culture-team-transport-19', 'car-culture-team-transport-20', 'car-culture-team-transport-21', 'car-culture-team-transport-23', 'car-culture-team-transport-25', 'car-culture-team-transport-27', 'car-culture-team-transport-28', 'car-culture-team-transport-30', 'car-culture-team-transport-31', 'car-culture-team-transport-32', 'car-culture-team-transport-33', 'car-culture-team-transport-36', 'car-culture-team-transport-38', 'car-culture-team-transport-43', 'car-culture-team-transport-52', 'car-culture-team-transport-56', 'car-culture-team-transport-70', 'car-culture-team-transport-71', 'car-culture-team-transport-74', 'car-culture-team-transport-78', 'car-culture-team-transport-80', 'car-culture-team-transport-84', 'car-culture-team-transport-86', 'car-culture-team-transport', 'car-culture-terra-trek', 'car-culture-thrill-climbers', 'car-culture-toyota', 'car-culture-track-day', 'car-culture-trucks', 'car-culture-world-tour'],
            'name': 'Car Culture'
        }
        # Adicione outras séries hierárquicas aqui
    }
    
    for main_series, config in hierarchical_consolidations.items():
        print(f"🔄 Consolidando hierarquicamente: {main_series}...")
        
        consolidated_data = {
            'series_id': main_series,
            'name': config['name'],
            'total_releases': 0,
            'max_index': 0,
            'releases': defaultdict(lambda: defaultdict(list))
        }
        
        # Processar cada sub-série
                # Processar cada sub-série
        for sub_series in config['sub_series']:
            sub_file = os.path.join(series_dir, f'{sub_series}.json')
            
            # SE o sub_series contém '/', procurar em subpastas
            if '/' in sub_series:
                sub_file = os.path.join(series_dir, f'{sub_series}.json')
            else:
                sub_file = os.path.join(series_dir, f'{sub_series}.json')
            
            if os.path.exists(sub_file):
                try:
                    with open(sub_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        
                        # Consolidar estatísticas
                        consolidated_data['total_releases'] += data.get('total_releases', 0)
                        consolidated_data['max_index'] = max(consolidated_data['max_index'], data.get('max_index', 0))
                        
                        # Organizar releases por ano e sub-série
                        # for year, releases in data.get('releases', {}).items():
                        #     # Remover duplicatas dos releases
                        #     unique_releases = list(set(releases))
                        #     consolidated_data['releases'][year][sub_series] = unique_releases

                                                # Organizar releases por ano e sub-série
                        releases_data = data.get('releases', [])
                        
                        # Se releases é uma lista (formato antigo), converter para dict
                        if isinstance(releases_data, list):
                            # Extrair ano do path do sub_series (ex: "1969/mainline" -> "1969")
                            year = sub_series.split('/')[0] if '/' in sub_series else 'unknown'
                            unique_releases = list(set(releases_data))  # Remover duplicatas
                            consolidated_data['releases'][year][sub_series] = unique_releases
                        else:
                            # Formato novo com dicionário
                            for year, releases in releases_data.items():
                                unique_releases = list(set(releases))
                                consolidated_data['releases'][year][sub_series] = unique_releases
                    
                    # Remover arquivo da sub-série
                    os.remove(sub_file)
                    print(f"  ✅ Integrado e removido: {sub_series}.json")
                    
                except Exception as e:
                    print(f"  ❌ Erro processando {sub_series}: {e}")
        
        # Converter defaultdict para dict normal
        consolidated_data['releases'] = {year: dict(sub_series_data) 
                                       for year, sub_series_data in consolidated_data['releases'].items()}
        
        # Salvar arquivo consolidado
               # Salvar arquivo consolidado
        main_file = os.path.join(series_dir, f'{main_series}.json')
        
        if os.path.exists(main_file):
            print(f"  ⚠️  Arquivo {main_series}.json já existe. Pulando...")
            continue

        # Garantir que o diretório existe
        os.makedirs(os.path.dirname(main_file), exist_ok=True)
        
        try:
            with open(main_file, 'w', encoding='utf-8') as f:
                json.dump(consolidated_data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"  ❌ Erro ao salvar {main_file}: {e}")
            continue  # Pula para o próximo se houver erro
        
        print(f"  🎯 Criado: {main_series}.json ({consolidated_data['total_releases']} releases em {len(consolidated_data['releases'])} anos)")

if __name__ == "__main__":
    consolidation()
    print("✅ Consolidação hierárquica concluída!")