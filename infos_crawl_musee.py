import os
import re

def merge_museum_data(crawl_museum_dir="pages_pertinentes_musees", output_dir="musee infos"):
    """
    Parcourt le dossier des musées crawlés, regroupe les informations de chaque musée
    dans un fichier unique par musée, en supprimant les doublons.

    Args:
        crawl_museum_dir (str): Chemin vers le dossier contenant les données brutes des musées.
                                 Ex: "pages_pertinentes_musees"
        output_dir (str): Chemin vers le dossier où les fichiers fusionnés seront sauvegardés.
                          Ex: "musee infos"
    """

    print(f"Démarrage du processus de fusion des données des musées...")
    print(f"Dossier source: '{crawl_museum_dir}'")
    print(f"Dossier de destination: '{output_dir}'\n")

    # Créer le dossier de sortie s'il n'existe pas
    os.makedirs(output_dir, exist_ok=True)
    print(f"Dossier de sortie '{output_dir}' créé ou déjà existant.\n")

    # Vérifier si le dossier source existe
    if not os.path.exists(crawl_museum_dir):
        print(f"ERREUR: Le dossier source '{crawl_museum_dir}' n'existe pas. Veuillez vérifier le chemin.")
        return

    # Parcourir chaque dossier de musée dans le répertoire principal
    museum_count = 0
    for museum_name in os.listdir(crawl_museum_dir):
        museum_path = os.path.join(crawl_museum_dir, museum_name)

        # S'assurer que c'est bien un dossier (et ignorer les fichiers éventuels à la racine)
        if not os.path.isdir(museum_path):
            continue

        museum_count += 1
        print(f"Traitement du musée: '{museum_name}'...")

        # Liste pour stocker les paragraphes uniques dans l'ordre d'apparition
        unique_paragraphs_ordered = []
        # Set pour détecter rapidement les doublons
        seen_paragraphs = set()

        # Parcourir tous les fichiers .md dans le dossier du musée
        files_in_museum_folder = os.listdir(museum_path)
        if not any(f.endswith(".md") for f in files_in_museum_folder):
            print(f"  ATTENTION: Aucun fichier '.md' trouvé dans le dossier '{museum_name}'.")
            continue

        for filename in files_in_museum_folder:
            if filename.endswith(".md"):
                file_path = os.path.join(museum_path, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # Diviser le contenu en paragraphes.
                    # Un paragraphe est défini par une ou plusieurs lignes vides.
                    # Utilisez re.split avec r'\n\s*\n+' pour gérer les multiples sauts de ligne
                    # et les espaces potentiels entre eux.
                    # strip() est important avant split pour éviter un paragraphe vide au début/fin
                    paragraphs = re.split(r'\n\s*\n+', content.strip())

                    for p in paragraphs:
                        # Nettoyer le paragraphe (supprimer les espaces en début/fin)
                        p_stripped = p.strip()
                        # Ajouter le paragraphe s'il n'est pas vide et n'a pas déjà été vu
                        if p_stripped and p_stripped not in seen_paragraphs:
                            unique_paragraphs_ordered.append(p_stripped)
                            seen_paragraphs.add(p_stripped)

                except UnicodeDecodeError:
                    print(f"  ATTENTION: Erreur d'encodage pour le fichier '{filename}'. Tentative avec 'latin-1'.")
                    try:
                        with open(file_path, 'r', encoding='latin-1') as f:
                            content = f.read()
                        paragraphs = re.split(r'\n\s*\n+', content.strip())
                        for p in paragraphs:
                            p_stripped = p.strip()
                            if p_stripped and p_stripped not in seen_paragraphs:
                                unique_paragraphs_ordered.append(p_stripped)
                                seen_paragraphs.add(p_stripped)
                    except Exception as e:
                        print(f"  ERREUR: Impossible de lire le fichier '{filename}' du musée '{museum_name}' avec 'latin-1': {e}")
                except Exception as e:
                    print(f"  ERREUR: Impossible de lire le fichier '{filename}' du musée '{museum_name}': {e}")

        # Écrire les informations regroupées dans un nouveau fichier pour ce musée
        if unique_paragraphs_ordered:
            output_file_name = f"{museum_name}.md" # Ou .txt si vous préférez un format texte pur
            output_file_path = os.path.join(output_dir, output_file_name)

            try:
                with open(output_file_path, 'w', encoding='utf-8') as f:
                    f.write(f"# Informations du Musée: {museum_name}\n\n")
                    f.write("--- \n\n") # Séparateur visuel

                    # Écrire chaque paragraphe unique, séparé par deux sauts de ligne pour une meilleure lisibilité
                    f.write("\n\n".join(unique_paragraphs_ordered))
                    f.write("\n") # Assurer une fin de fichier propre
                print(f"  Informations fusionnées et sauvegardées dans '{output_file_name}'.")
            except Exception as e:
                print(f"  ERREUR: Impossible d'écrire le fichier de sortie pour '{museum_name}': {e}")
        else:
            print(f"  Aucune information unique trouvée pour le musée '{museum_name}'. Fichier non créé.")
        print("-" * 50) # Séparateur pour la console

    if museum_count == 0:
        print(f"\nAucun dossier de musée trouvé dans '{crawl_museum_dir}'. Assurez-vous que le chemin est correct et qu'il contient des dossiers de musées.")
    else:
        print(f"\nFusion de données terminée pour {museum_count} musées. Les fichiers sont dans le dossier '{output_dir}'.")

# --- Exécution du script ---
if __name__ == "__main__":
    # Assurez-vous que le dossier 'pages_pertinentes_musees' existe au même niveau que votre script
    # ou spécifiez le chemin complet si ce n'est pas le cas.
    merge_museum_data()

    # Exemple si votre dossier 'pages_pertinentes_musees' est à un autre emplacement:
    # merge_museum_data("/chemin/vers/votre/dossier/pages_pertinentes_musees", "musee infos")