#!/usr/bin/env python3
"""
Script de nettoyage automatique des branches exercices
"""

import subprocess
import os

def run_git_command(cmd):
    """Exécuter une commande git"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Erreur: {result.stderr}")
    return result.returncode == 0

def clean_exercise_branch(exercise_num):
    """Nettoyer une branche exercice spécifique"""
    branch_name = f"exercice{exercise_num}"
    print(f"🧹 Nettoyage de {branch_name}...")
    
    # Checkout vers la branche
    if not run_git_command(f"git checkout {branch_name}"):
        print(f"❌ Impossible de passer à {branch_name}")
        return False
    
    # Fichiers à supprimer (communs à toutes les branches)
    files_to_remove = [
        "DEVELOPMENT_ROADMAP.md",
        "DOCKER_GUIDE.md", 
        "FINAL_STATUS.md",
        "GITHUB_SUCCESS.md",
        "GUIDE_CONTINUITE.md",
        "PROJECT_README.md",
        "hello-world-test.bat",
        "setup-environment.ps1",
        "BRANCHES_STRATEGY.md",
        "create-exercise-branches.ps1",
        "test_exercice1.py",
        "test_exercice2.py", 
        "test_final.py",
        "test_global.py",
        "test-global.bat",
        "start-services.ps1",
        "NAVIGATION.md"
    ]
    
    # Supprimer les fichiers s'ils existent
    for file in files_to_remove:
        if os.path.exists(file):
            try:
                os.remove(file)
                print(f"  ✅ Supprimé: {file}")
            except Exception as e:
                print(f"  ⚠️ Erreur suppression {file}: {e}")
    
    # Commiter les changements
    run_git_command("git add -A")
    commit_success = run_git_command(f'git commit -m "Clean {branch_name}: Remove non-essential files, keep only exercise-specific content"')
    
    if commit_success:
        print(f"✅ {branch_name} nettoyé et committé")
    else:
        print(f"⚠️ {branch_name} - Aucun changement ou erreur commit")
    
    return True

def main():
    """Nettoyer tous les exercices"""
    print("🚀 NETTOYAGE AUTOMATIQUE DES EXERCICES")
    print("=" * 50)
    
    # Nettoyer les exercices 3 à 8 (1 et 2 déjà fait)
    for i in range(3, 9):
        clean_exercise_branch(i)
        print()
    
    # Retourner à main
    print("🔄 Retour à la branche main...")
    run_git_command("git checkout main")
    
    print("✅ NETTOYAGE TERMINÉ!")
    print("\n📋 Actions suivantes recommandées:")
    print("  git push origin exercice1 exercice2 exercice3 exercice4 exercice5 exercice6 exercice7 exercice8 -f")

if __name__ == "__main__":
    main()