Write-Host "🚀 Backend kurulumu"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt

Write-Host "🚀 Frontend kurulumu"
cd frontend
npm install
cd ..
Write-Host "✅ Kurulum tamamlandı!"
