import os
import json
import ollama
from tqdm import tqdm
import re
import shutil # Pour copier les fichiers

# --- Configuration ---
# Chemin vers votre dossier parent qui contient les dossiers de chaque musée
MUSEUM_PAGES_DIR = r'C:\Users\victo\Desktop\crawl\crawl_output'

# Nom du modèle Ollama à utiliser (doit être téléchargé et disponible via Ollama)
OLLAMA_MODEL = 'gemma3:4b'

# Adresse de votre serveur Ollama (par défaut). Ne changez que si nécessaire.
OLLAMA_HOST = 'http://localhost:11434'

# Fichier pour enregistrer les résultats de l'évaluation
OUTPUT_FILE = 'scores_evaluation_musees.json'

# Limite la longueur du texte envoyé à l'LLM pour éviter de dépasser le contexte
# ou de consommer trop de tokens.
MAX_TEXT_LENGTH_TO_SEND = 10000 # caractères

# --- Configuration pour la copie des fichiers pertinents ---
# Seuil de score minimum pour considérer une page comme "élevée" et la copier
SCORE_THRESHOLD = 70 # Par exemple, toutes les pages avec un score >= 70 seront copiées

# Dossier où seront copiées les pages pertinentes
PERTINENT_PAGES_DIR = './pages_pertinentes_musees'

# --- Fonction pour extraire le texte d'un fichier Markdown (.md) ---
def extract_text_from_md(filepath):
    """
    Extrait le texte brut d'un fichier Markdown.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()
        return text
    except UnicodeDecodeError:
        print(f"AVERTISSEMENT: Impossible de décoder '{filepath}' avec UTF-8. Essai avec ISO-8859-1.")
        try:
            with open(filepath, 'r', encoding='iso-8859-1') as f:
                text = f.read()
            return text
        except Exception as e:
            print(f"ERREUR: Impossible de lire '{filepath}'. Erreur: {e}")
            return None
    except Exception as e:
        print(f"ERREUR: Problème lors de l'extraction du texte de '{filepath}'. Erreur: {e}")
        return None

# --- Fonction pour obtenir le score de l'LLM (inchangée) ---
def get_museum_relevance_score(text_content, ollama_client):
    """
    Interroge le modèle Gemma via Ollama pour obtenir un score de pertinence
    par rapport à des informations muséales ou artistiques.
    Le score est un entier entre 0 et 99.
    """
    if not text_content or len(text_content.strip()) < 100: # Minimum de texte pour une évaluation pertinente
        return 0, "Texte trop court ou vide pour évaluation significative."

    # Tronquer le texte si nécessaire avant de l'envoyer à l'LLM
    processed_text = text_content[:MAX_TEXT_LENGTH_TO_SEND]

    prompt = f"""
    En tant qu'expert en musées, en histoire de l'art et en patrimoine culturel, votre mission est d'évaluer la pertinence d'une page web.
    La pertinence est définie par la présence d'informations directement liées aux musées, aux œuvres d'art, aux expositions,
    aux collections permanentes ou temporaires, aux artistes, à l'histoire de l'art, à des événements culturels spécifiques
    organisés par des institutions muséales, ou à toute autre donnée fondamentale pour le domaine muséal et artistique.

    Le score doit être un nombre entier entre 0 et 99, sans aucun texte, explication, ponctuation ou formatage supplémentaire :
    -   0 : La page n'est absolument pas pertinente. Exemples : pages d'erreur, sites commerciaux génériques, blogs personnels sans lien avec l'art/musées, pages de spam.
    -   1-29 : Très faible pertinence. Exemples : mentions très brèves d'un musée dans un contexte non artistique, pages de contact génériques sans informations sémantiques.
    -   30-49 : Faible à moyenne pertinence. Exemples : articles de presse généraux mentionnant un musée sans détails substantiels, blogs culturels non spécialisés.
    -   50-69 : Moyenne pertinence. Exemples : page "À propos" d'un musée (informations générales), page de billetterie (informations fonctionnelles mais peu de contenu muséal), articles de blog sur l'art mais pas très approfondis.
    -   70-89 : Bonne pertinence. Exemples : descriptions de salles ou d'espaces au sein d'un musée, listes d'œuvres d'art sans descriptions détaillées, actualités d'expositions courtes.
    -   90-99 : Très haute pertinence. Exemples : pages officielles de musées avec descriptions détaillées d'œuvres, d'expositions majeures, d'artistes, ou de l'histoire du musée. Contenu riche et spécifique au domaine muséal.

    Votre réponse DOIT être UNIQUEMENT un nombre entier entre 0 et 99.

    Contenu de la page web à évaluer :
    ---
    {processed_text}
    ---
    Score :
    """

    try:
        response = ollama_client.chat(
            model=OLLAMA_MODEL,
            messages=[{'role': 'user', 'content': prompt}],
            stream=False # Attendre la réponse complète
        )

        llm_response_content = response['message']['content'].strip()

        # Utiliser une regex plus stricte pour s'assurer que seul un nombre est extrait
        match = re.fullmatch(r'(0|[1-9][0-9]?)', llm_response_content) # Cherche un match exact de 0-99
        if match:
            score = int(match.group(0))
            if 0 <= score <= 99:
                return score, "Succès"
            else:
                return 0, f"Score hors limites renvoyé par l'LLM: {llm_response_content}"
        else:
            strict_match = re.search(r'\b(0|[1-9][0-9]?|99)\b', llm_response_content)
            if strict_match:
                return int(strict_match.group(1)), f"Succès (extraction non stricte): {llm_response_content}"
            else:
                return 0, f"Impossible d'extraire un score numérique valide de la réponse LLM: '{llm_response_content}'"

    except ollama.ResponseError as e:
        return 0, f"Erreur de réponse Ollama: {e}. Vérifiez la configuration du modèle et du serveur."
    except ollama.RequestError as e:
        return 0, f"Erreur de connexion Ollama: {e}. Assurez-vous qu'Ollama est en cours d'exécution sur {OLLAMA_HOST}."
    except Exception as e:
        return 0, f"Erreur inattendue lors de l'appel LLM: {e}"

# --- Script principal ---
def main():
    if not os.path.isdir(MUSEUM_PAGES_DIR):
        print(f"Erreur: Le dossier '{MUSEUM_PAGES_DIR}' n'existe pas. Veuillez vérifier le chemin.")
        return

    # Créer le dossier pour les pages pertinentes s'il n'existe pas
    os.makedirs(PERTINENT_PAGES_DIR, exist_ok=True)
    print(f"Les pages pertinentes seront copiées dans '{PERTINENT_PAGES_DIR}' (score >= {SCORE_THRESHOLD}).")

    print(f"Démarrage de l'évaluation des pages de musées dans '{MUSEUM_PAGES_DIR}'...")
    print(f"Modèle Ollama utilisé: {OLLAMA_MODEL}")
    print(f"Hôte Ollama: {OLLAMA_HOST}")
    print(f"Les résultats de l'évaluation seront sauvegardés dans: '{OUTPUT_FILE}'")
    print(f"Longueur maximale du texte envoyé à l'LLM: {MAX_TEXT_LENGTH_TO_SEND} caractères")


    results = []
    total_pages_to_process = 0

    # Compter le nombre total de pages .md pour la barre de progression
    print("Comptage des fichiers Markdown...")
    for root, _, files in os.walk(MUSEUM_PAGES_DIR):
        for file in files:
            if file.endswith('.md'): # Changement ici: cibler les fichiers .md
                total_pages_to_process += 1

    if total_pages_to_process == 0:
        print("Aucun fichier .md trouvé dans le répertoire spécifié. Le script s'arrête.")
        return

    print(f"Total de {total_pages_to_process} pages Markdown à évaluer.")

    ollama_client = ollama.Client(host=OLLAMA_HOST)

    with tqdm(total=total_pages_to_process, desc="Progression de l'évaluation") as pbar:
        for root, dirs, files in os.walk(MUSEUM_PAGES_DIR):
            dirs[:] = [d for d in dirs if not d.startswith(('.', '_'))]

            if root == MUSEUM_PAGES_DIR:
                museum_folder_name = "ROOT_CRAWL_MUSEE"
            else:
                museum_folder_name = os.path.basename(root)

            for file_name in files:
                if file_name.endswith('.md'): # Changement ici: cibler les fichiers .md
                    file_path = os.path.join(root, file_name)

                    text_content = extract_text_from_md(file_path) # Appel à la nouvelle fonction d'extraction MD

                    score = 0
                    status_message = "Non évalué"

                    if text_content:
                        score, status_message = get_museum_relevance_score(text_content, ollama_client)
                    else:
                        status_message = "Impossible d'extraire le texte de la page ou texte vide."

                    results.append({
                        'museum_folder': museum_folder_name,
                        'page_filename': file_name,
                        'full_path': file_path,
                        'score': score,
                        'status': status_message
                    })

                    # --- Logique de copie des pages pertinentes ---
                    if score >= SCORE_THRESHOLD:
                        # Créer un chemin relatif pour recréer l'arborescence dans le dossier de destination
                        relative_path = os.path.relpath(file_path, MUSEUM_PAGES_DIR)
                        dest_path = os.path.join(PERTINENT_PAGES_DIR, relative_path)
                        
                        # Assurer que le répertoire de destination existe
                        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                        
                        try:
                            shutil.copy2(file_path, dest_path) # copy2 conserve les métadonnées (timestamps, etc.)
                            # print(f"Copié '{file_name}' (score {score}) vers '{dest_path}'") # Pour débogage, peut être bruyant
                        except Exception as e:
                            print(f"ERREUR: Impossible de copier '{file_name}' vers '{dest_path}'. Erreur: {e}")

                    pbar.update(1)

    # Sauvegarder les résultats dans un fichier JSON
    try:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=4, ensure_ascii=False)
        print(f"\nÉvaluation terminée ! Les résultats ont été sauvegardés dans '{OUTPUT_FILE}'")
        print(f"Nombre total de pages évaluées: {len(results)}")
        print(f"Vérifiez le dossier '{PERTINENT_PAGES_DIR}' pour les pages avec un score >= {SCORE_THRESHOLD}.")
    except Exception as e:
        print(f"ERREUR: Impossible de sauvegarder les résultats dans '{OUTPUT_FILE}'. Erreur: {e}")

if __name__ == "__main__":
    main()