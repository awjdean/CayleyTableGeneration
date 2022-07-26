git
# GitHub

* git add .
  - Saves the changes (locally) as a checkpoint to the branch you are currently in.

* *Commit:* git commit -m "insert notes here"

* *Branches:* git branch -M main
  - *Create new branch:* git checkout -b <branch_name>
  * *Merge branches:*
    1. Switch to main branch: git checkout main
    2. Git pull: git pull
    3. Switch into other branch: git checkout <branch_name>
    4. Sync commit histories and merge: git rebase main
       - This merges branch main into branch branch_name.
       - main is the name of the branch
    5. Git push <branch_name>
    6. Go to GitHub 

* *Push:* git push -u origin <main>
  - Sends local changes to remote (GitHub).
  - Origin is a shortcut to the name of the remote repo.
  - Main is the name of the branch

* *Pull:* git pull (-u origin main (?))
  - Sends remote changes to local.

  