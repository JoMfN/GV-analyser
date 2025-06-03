---
title: GV-Label-Analyser
sdk: streamlit
sdk_version: 1.44.0
app_file: appV1.py
license: mit
short_description: App analyzing images using Gemini AI Vision.
python version=3.11
---


---
## Install

Use Conda > See Miniconda-linux oneliner

```bash
git clone https://github.com/JoMfN/GV-analyser.git
```

--- 

```bash
conda create -n GVanalyser python=3.11 -y
```

---


```bash
cd GV-analyser
conda activate GVanalyser
pip install -r requirements.txt
```

update Pip if prompted

## Setup Key

Create a .env_1 file with a API key just pasted within it 

your key could be `AIzaSyXXXXXX`

then 

```bash
nano .env_1
```

paste key

> paste key `.env_1` terminal

```
AIzaSyXXXXXX
```

press [CTRL + C]

should fix any API errors at the start.

## Fire it up

```bash
streamlit run appV1.py
```

Navigate to `localhost:8501` in your browser


[localhost:8501](http://localhost:8501)

