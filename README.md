# お絵描きバトラー

## Gitの使い方
### レポジトリのクローン
`git clone git@github.com:shiyow5/OekakiBattler.git`  

### リモート→ローカル
`git pull origin <ブランチ名>`

### ブランチの作成
`git switch -c <ブランチ名>`  

### ブランチの切り替え
`git switch <ブランチ名>`  

### ローカル→リモート
`git push origin <ブランチ名>`

### ステージング（変更を選択）
`git add <ファイル名>`  
※ `git add .` ですべてのファイルを選択  

### コミット
`git commit -m <メッセージ>`

### 具体的なローカル→リモートの流れ(例)
1. ファイルを編集(キリのいいところまで)
2. ステージング
3. コミット
4. プッシュ
```git
git switch -c Test  #ブランチ切る
touch ファイル.txt  #何かしら作業（今回の例はファイルを作っただけ）
git add .
git commit -m "新規ファイルを追加"
git push origin Test
```

## 参考リンク
[【ゲーム作成】Pythonでいらすとやのスマブラ風ゲームを作ります【pygame】](https://it-programming-beginner.com/2023/08/23/pygame-ssbu-01/)  
[格闘ゲームをPygameで自作してみる](https://note.com/kakunik/n/n899af1ce8bfd) ← これ大事  
[pygameを用いて簡単な格闘ゲームを自作してみた](https://qiita.com/kankitu_man/items/0c47e24aff11fee9022c)  
