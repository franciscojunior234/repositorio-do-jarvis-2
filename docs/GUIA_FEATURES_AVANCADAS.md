# 🤖 JARVIS - Guia de Novas Features Avançadas

## 📦 Instalação de Dependências

### Passo 1: Atualizar requirements.txt
```bash
pip install -r requirements.txt
```

### Passo 2: Dependências Opcionais (por Feature)

#### Para IoT - Casa Inteligente
```bash
pip install paho-mqtt aiohttp
```

#### Para Reconhecimento Facial
```bash
pip install opencv-python opencv-contrib-python dlib face-recognition
```

#### Para Base de Conhecimento
```bash
pip install wikipediaapi google-search-results pinecone-client
```

#### Para Machine Learning Avançado
```bash
pip install transformers torch scikit-learn numpy pandas
```

---

## 🚀 Como Usar as Novas Features

### 1️⃣ Sistema de Aprendizado Persistente

```python
from app.ml import learning_engine

# Registrar uma interação
learning_engine.add_interaction(
    user_id="user_001",
    command="Como está o tempo?",
    response="Está ensolarado com 25°C",
    feedback=0.9,  # Score de satisfação (0-1)
    context={"location": "São Paulo"}
)

# Recuperar contexto do usuário
context = learning_engine.get_user_context("user_001")

# Buscar interações similares
similares = learning_engine.recall_similar_interactions(
    query="Qual é o tempo?",
    user_id="user_001"
)

# Personalizar resposta
resposta_personalizada = learning_engine.personalize_response(
    user_id="user_001",
    response="Olá, estimado usuário"
)

# Ver estatísticas
stats = learning_engine.get_learning_stats()
print(stats)
```

### 2️⃣ Controle de Casa Inteligente (IoT)

#### Conectar ao MQTT Broker

```python
from app.iot import MQTTClient, SmartHomeManager

# Inicializar cliente MQTT
mqtt = MQTTClient(
    broker_host="localhost",  # ou IP do seu broker
    broker_port=1883,
    client_id="jarvis-iot"
)

# Conectar
if mqtt.connect():
    print("✅ Conectado ao MQTT")
else:
    print("❌ Erro ao conectar")

# Registrar dispositivos
mqtt.register_device("light_01", "light", "Luz da Sala", ["on", "off", "dim"])
mqtt.register_device("thermo_01", "thermostat", "Ar Condicionado", ["heat", "cool"])

# Criar gerenciador de casa inteligente
manager = SmartHomeManager(mqtt)

# Executar comando de voz
resultado = manager.execute_voice_command("Ligar as luzes da sala")
print(resultado)  # ✅ 1 lâmpada(s) acesa(s)

# Publicar comando direto
mqtt.publish_command(
    device_id="light_01",
    command="turn_on"
)

# Obter estado do dispositivo
estado = mqtt.get_device_state("light_01")

# Desconectar
mqtt.disconnect()
```

#### Dispositivos Suportados
- 💡 **Light** (Lâmpadas inteligentes)
- 🌡️ **Thermostat** (Ar condicionado/Aquecedor)
- 🔐 **Security** (Câmeras, fechaduras)
- 📺 **Entertainment** (TV, som)

### 3️⃣ Base de Conhecimento

```python
from app.knowledge import knowledge_base, SemanticSearch

# Buscar no Wikipedia
resultado = knowledge_base.search_wikipedia("Inteligência Artificial")
print(resultado["summary"])

# Buscar no Google
resultados = knowledge_base.search_google("últimas notícias de IA", num_results=5)

# Responder pergunta com busca automática
resposta = knowledge_base.answer_question("Quem inventou o Python?")

# Busca Semântica
semantic = SemanticSearch()
semantic.add_document("doc1", "Python é uma linguagem de programação")
semantic.add_document("doc2", "JavaScript é para desenvolvimento web")

resultados = semantic.search("linguagens de programação", top_k=5)

# Ver estatísticas de cache
stats = knowledge_base.get_stats()
```

### 4️⃣ Reconhecimento Facial

```python
from app.vision import FaceDetector, FaceRecognizer, init_face_recognition

# Inicializar
init_face_recognition()

# Detectar rostos em imagem
from app.vision import face_detector
rostos = face_detector.detect_faces("foto.jpg")
# Output: [{"x": 100, "y": 120, "width": 50, "height": 60, "area": 3000}]

# Registrar nova pessoa
from app.vision import face_recognizer
face_recognizer.register_face("João Silva", "foto_joao.jpg")

# Reconhecer pessoas em imagem
resultados = face_recognizer.recognize_faces("foto_grupo.jpg")
# Output: [
#   {"name": "João Silva", "confidence": 0.95, "location": {...}},
#   {"name": "Desconhecido", "confidence": 0.0, "location": {...}}
# ]

# Listar pessoas registradas
pessoas = face_recognizer.get_all_known_people()
print(pessoas)  # ["João Silva", "Maria Santos"]

# Detectar rostos da câmera em tempo real
rostos_camera = face_detector.detect_from_camera()
```

---

## 📊 Estrutura de Diretórios

```
JARVIS-IA/
├── app/
│   ├── ml/                    # Machine Learning
│   │   ├── __init__.py
│   │   └── learning_engine.py
│   │
│   ├── iot/                   # IoT & Smart Home
│   │   ├── __init__.py
│   │   └── mqtt_client.py
│   │
│   ├── vision/                # Visão Computacional
│   │   ├── __init__.py
│   │   └── face_recognition.py
│   │
│   ├── knowledge/             # Base de Conhecimento
│   │   ├── __init__.py
│   │   └── knowledge_base.py
│   │
│   └── data/                  # Dados Persistentes
│       ├── learning_db.json
│       ├── knowledge_cache.json
│       ├── known_faces/       # Fotos para reconhecimento
│       └── faces_db.json
│
└── demo_advanced_features.py  # Demonstração
```

---

## 🧪 Rodar Demonstração

```bash
python demo_advanced_features.py
```

Isto vai executar exemplos de:
1. Aprendizado Persistente
2. Controle IoT
3. Base de Conhecimento
4. Reconhecimento Facial

---

## 🔧 Configuração MQTT (Opcional)

Se você quer testar IoT, instale um broker MQTT:

### Mosquitto (Recomendado)
```bash
# Windows
choco install mosquitto  # ou baixe em mosquitto.org

# Linux
sudo apt-get install mosquitto mosquitto-clients

# macOS
brew install mosquitto
```

### Iniciar Broker
```bash
mosquitto -v
```

Agora você pode conectar ao `localhost:1883`

---

## 📝 Próximas Implementações

- [ ] Fine-tuning com dados do usuário
- [ ] Detecção de emoção em tempo real
- [ ] Integração com Home Assistant
- [ ] Speech Recognition avançado (Faster-Whisper)
- [ ] Dashboard 3D em React
- [ ] Aprendizado por Reinforcement Learning

---

## ⚠️ Troubleshooting

### ImportError: No module named 'face_recognition'
```bash
pip install face-recognition
```

### ImportError: No module named 'paho.mqtt'
```bash
pip install paho-mqtt
```

### Erro ao conectar MQTT
- Verifique se o broker está rodando: `mosquitto -v`
- Verifique host/port em `MQTTClient(broker_host="localhost")`
- Confira firewall

### Câmera não encontrada
- Verifique se tem câmera conectada
- Tente: `python -c "import cv2; cv2.VideoCapture(0).isOpened()"`

---

## 📖 Documentação Adicional

- [Hugging Face Transformers](https://huggingface.co/transformers/)
- [MQTT Documentation](https://mqtt.org/)
- [OpenCV Docs](https://docs.opencv.org/)
- [Face Recognition](https://github.com/ageitgey/face_recognition)

---

**Desenvolvido com ❤️ para o JARVIS**
