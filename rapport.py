import os
import re
import time

def generate_report():
    results_dir = "bible_kirundi_versets"
    
    # Noms des livres en kirundi (66 livres)
    books_kirundi = [
        "Itanguriro", "Kuvayo", "Abalewi", "Guharura", "Gusubira mu vyagezwe",
            "Yosuwa", "Abacamanza", "Rusi", "Samweli wa mbere", "Samweli wa kabiri",
            "Abami ba mbere", "Abami ba kabiri", "Ngoma za mbere", "Ngoma za kabiri", "Ezira", "Nehemiya",
            "Esiteri", "Yobu", "Zaburi", "Imigani", "Umusiguzi", "Indirimbo ya Salomo",
            "Yesaya", "Yeremiya", "Gucura intimba", "Ezekiyeli", "Daniyeli", "Hoseya",
            "Yoweli", "Amosi", "Obadiya", "Yona", "Mika", "Nahumu", "Habakuki",
            "Zefaniya", "Hagayi", "Zakariya", "Malaki", "Matayo", "Mariko",
            "Luka", "Yohani", "Ivyakozwe n intumwa", "Abaroma", "Abakorinto ba mbere", "Abakorinto ba kabiri",
            "Abagalatiya", "Abanyefeso", "Abafilipi", "Abakolosayi", "Abatesalonika ba mbere", "Abatesalonika ba kabiri",
            "Timoteyo wa mbere", "Timoteyo wa kabiri", "Tito", "Filemoni", "Abaheburayo", "Ikete rya Yakobo",
            "Petero wa mbere", "Petero wa kabiri", "Yohani wa mbere", "Yohani wa kabiri", "Yohani wa gatatu", "Ikete rya Yuda",
            "Ivyahishuriwe Yohani"
    ]

    # Nombre de chapitres par livre (Genèse à Apocalypse)
    chapters_per_book = [
        50, 40, 27, 36, 34, 24, 21, 4, 31, 24,
        22, 25, 29, 36, 10, 13, 10, 42, 150, 31,
        12, 8, 66, 52, 5, 48, 12, 14, 3, 9,
        1, 4, 7, 3, 3, 3, 2, 14, 4, 28,
        16, 24, 21, 28, 16, 16, 13, 6, 6, 4,
        4, 5, 3, 6, 4, 3, 1, 13, 5, 5, 3, 5, 1, 1, 1, 22
    ]

    print("📊 Génération du rapport à partir des fichiers existants...")
    report = "# Rapport de Scraping - Bible Kirundi (Tout les livres)\n"
    report += "## Résumé Global\n"
    report += f"- **Date du scraping**: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"

    total_books = len(books_kirundi)
    total_verses = 0
    successful_books = 0
    failed_books = []

    report += "| Livre | Chapitres attendus | Versets | Statut |\n"
    report += "|-------|------------------|----------|--------|\n"

    for i, book_name in enumerate(books_kirundi):
        filename = f"{results_dir}/{book_name.replace(' ', '_')}.md"
        expected_chapters = chapters_per_book[i] if i < len(chapters_per_book) else 0

        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                content = f.read()
                verse_count = len(re.findall(r'\*\*(\d+)\.\*\*', content))
                chapter_count = len(set(re.findall(r'##.*?(\d+)', content)))
                status = "✅ Réussi"
                successful_books += 1
                total_verses += verse_count
        else:
            verse_count = 0
            chapter_count = 0
            status = "❌ Échec"

        report += f"| {book_name} | {expected_chapters} | {verse_count} | {status} |\n"

        if status == "❌ Échec":
            failed_books.append(book_name)

    report += "\n## Détails détaillés\n"
    if failed_books:
        report += "### Livres ayant échoué\n"
        for book in failed_books:
            report += f"- {book}\n"
    else:
        report += "- ✅ Aucun livre n'a complètement échoué\n"

    report += "\n## Statistiques générales\n"
    report += f"- **Livres réussis**: {successful_books}/{total_books}\n"
    report += f"- **Total versets extraits**: {total_verses}\n"

    # Sauvegarder le rapport final
    os.makedirs(results_dir, exist_ok=True)
    report_path = f"{results_dir}/RAPPORT_SCRAPING_BIBLE_FINAL.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"\n🏁 Rapport généré avec succès !")
    print(f"✅ Livres réussis: {successful_books}/{total_books}")
    print(f"📖 Total versets extraits: {total_verses}")
    print(f"📁 Rapport sauvegardé dans : {report_path}")

if __name__ == "__main__":
    generate_report()