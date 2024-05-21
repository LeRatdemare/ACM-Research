# GitHub du stage de Nathan et Simon

## Tuto Git/Github

### Créer un nouveau projet

- \[terminal\] `git init` ===> Créer un nouveau projet git vierge (globalement, on évite)
- \[terminal\] `git clone "https://github.com/LeRatdemare/ACM-Research.git"` ===> Cloner un dépôt distant existant (à faire de préférence)

### Travailler

Les étapes 1 à 3 sont à effectuer avant ET après chaque session de travail. L'étape 4 ne s'effectue qu'après avoir rajouté des modifications.

1. (optionnel) \[terminal\] `git add .`===> Ajouter tous les fichiers modifiés/nouveaux au stage (local)
2. (optionnel) \[terminal\] `git commit -m "Mon message"`===> Commit les fichiers = nouvelle version du projet (local)
3. \[terminal\] `git pull --rebase origin main`===> Mettre à jour son dépôt local
   - Equivalent : `git pull --rebase`
   - S'il y a un conflit, faire :
     1. `git rebase --abort`
     2. `git pull`
     3. Résoudre le conflit à la main
4. \[terminal\] `git push origin main`===> Mettre à jour le dépôt distant (Github)
   - Equivalent : `git push`

## Pense-bête

### Raccourcis clavier
