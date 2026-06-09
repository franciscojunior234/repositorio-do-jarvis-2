import { useCallback, useEffect, useMemo, useRef, useState } from "react";

const API_URL = "http://127.0.0.1:8765";

export default function JarvisDashboard({ currentUser, onLogout }) {
  const [apiOnline, setApiOnline] = useState(false);
  const messagesStorageKey = useMemo(
    () => `jarvis.messages.${currentUser?.id ?? "default"}`,
    [currentUser?.id],
  );

  const [messages, setMessages] = useState(() => {
    const stored = localStorage.getItem(messagesStorageKey);
    if (stored) {
      try {
        return JSON.parse(stored).map((message) => ({
          ...message,
          time: new Date(message.time),
        }));
      } catch {
        return [];
      }
    }

    return [
      {
        id: crypto.randomUUID(),
        role: "jarvis",
        text: "Verificando conexao com a API Python...",
        source: "system",
        time: new Date(),
      },
    ];
  });

  const [input, setInput] = useState("");
  const [isSending, setIsSending] = useState(false);
  const [voiceEnabled, setVoiceEnabled] = useState(true);
  const [cameraEnabled, setCameraEnabled] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const inputRef = useRef(null);
  const messagesRef = useRef(null);
  const recognitionRef = useRef(null);

  const browserCanListen = useMemo(
    () => Boolean(getSpeechRecognition()),
    [],
  );

  const updateSystemMessage = useCallback((text, source) => {
    setMessages((current) => {
      if (current.length === 0) {
        return [
          {
            id: crypto.randomUUID(),
            role: "jarvis",
            text,
            source,
            time: new Date(),
          },
        ];
      }

      const [firstMessage, ...rest] = current;

      if (firstMessage.source !== "system" && firstMessage.source !== "error") {
        return current;
      }

      return [
        {
          ...firstMessage,
          text,
          source,
          time: new Date(),
        },
        ...rest,
      ];
    });
  }, []);

  const checkStatus = useCallback(async () => {
    try {
      const response = await fetch(`${API_URL}/api/status`);
      setApiOnline(response.ok);

      if (response.ok) {
        updateSystemMessage(
          "API Python conectada. Minhas funcoes ja estao disponiveis.",
          "system",
        );
      }
    } catch {
      setApiOnline(false);
      updateSystemMessage(
        "API Python offline. Rode: python api_server.py",
        "error",
      );
    }
  }, [updateSystemMessage]);

  useEffect(() => {
    const timeout = window.setTimeout(checkStatus, 0);
    const interval = window.setInterval(checkStatus, 5000);
    return () => {
      window.clearTimeout(timeout);
      window.clearInterval(interval);
    };
  }, [checkStatus]);

  useEffect(() => {
    messagesRef.current?.scrollTo({
      top: messagesRef.current.scrollHeight,
      behavior: "smooth",
    });
  }, [messages]);

  useEffect(() => {
    localStorage.setItem(messagesStorageKey, JSON.stringify(messages));
  }, [messages, messagesStorageKey]);

  async function submitCommand(text) {
    if (!text || isSending) {
      return;
    }

    setInput("");
    addMessage("user", text, "user");
    setIsSending(true);

    try {
      const response = await fetch(`${API_URL}/api/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: text,
          speak: voiceEnabled,
          user_id: currentUser?.id,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        addMessage("jarvis", data.error ?? "Falha ao executar comando.", "error");
        return;
      }

      addMessage("jarvis", data.response, data.source);
      setApiOnline(true);
    } catch {
      setApiOnline(false);
      addMessage(
        "jarvis",
        "Nao consegui conectar na API Python. Rode: python api_server.py",
        "error",
      );
    } finally {
      setIsSending(false);
    }
  }

  async function sendMessage(event) {
    event?.preventDefault();
    await submitCommand(input.trim());
  }

  async function listenWithBackend(reason = "fallback") {
    if (isSending) {
      return;
    }

    setIsListening(true);
    addMessage(
      "jarvis",
      reason === "network"
        ? "A voz do navegador falhou por rede. Vou escutar pelo backend Python."
        : "Vou escutar pelo backend Python.",
      "system",
    );

    try {
      const response = await fetch(`${API_URL}/api/listen`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          speak: voiceEnabled,
          user_id: currentUser?.id,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        addMessage(
          "jarvis",
          data.error ?? "Nao consegui ouvir pelo backend Python.",
          "error",
        );
        return;
      }

      if (data.transcript) {
        addMessage("user", data.transcript, "voice");
      }

      addMessage("jarvis", data.response, data.source);
      setApiOnline(true);
    } catch {
      setApiOnline(false);
      addMessage(
        "jarvis",
        "Nao consegui conectar ao backend para ouvir pelo microfone.",
        "error",
      );
    } finally {
      setIsListening(false);
    }
  }

  function addMessage(role, text, source) {
    setMessages((current) => [
      ...current,
      {
        id: crypto.randomUUID(),
        role,
        text,
        source,
        time: new Date(),
      },
    ]);
  }

  function clearMessages() {
    setMessages([]);
  }

  function exportConversation() {
    const content = messages
      .map((message) => {
        const author = message.role === "user" ? "Voce" : "Jarvis";
        return `[${formatTime(message.time)}] ${author}: ${message.text}`;
      })
      .join("\n");

    const blob = new Blob([content], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "conversa-jarvis.txt";
    link.click();
    URL.revokeObjectURL(url);
  }

  async function startBrowserListening() {
    if (isListening) {
      return;
    }

    const SpeechRecognition = getSpeechRecognition();

    if (!SpeechRecognition) {
      await listenWithBackend("unsupported");
      return;
    }

    if (!navigator.mediaDevices?.getUserMedia) {
      addMessage(
        "jarvis",
        "O navegador nao liberou acesso ao microfone nesta pagina.",
        "error",
      );
      return;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      stream.getTracks().forEach((track) => track.stop());
    } catch {
      addMessage(
        "jarvis",
        "Permissao do microfone negada. Libere o microfone no navegador e toque em MIC novamente.",
        "error",
      );
      return;
    }

    recognitionRef.current?.abort();

    const recognition = new SpeechRecognition();
    recognitionRef.current = recognition;

    recognition.lang = "pt-BR";
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;
    recognition.continuous = false;
    recognition.onstart = () => {
      setIsListening(true);
      addMessage("jarvis", "Estou ouvindo. Pode falar o comando.", "system");
    };
    recognition.onend = () => {
      setIsListening(false);
      recognitionRef.current = null;
    };
    recognition.onerror = (event) => {
      const messagesByError = {
        "not-allowed": "Permissao do microfone bloqueada pelo navegador.",
        "no-speech": "Nao ouvi nenhum comando. Toque em MIC e tente falar de novo.",
        "audio-capture": "Nao encontrei um microfone ativo neste computador.",
        network: "O reconhecimento de voz do navegador falhou por rede.",
      };

      addMessage("jarvis", "Nao consegui acessar o microfone do navegador.", "error");
      addMessage(
        "jarvis",
        messagesByError[event.error] ?? `Erro de microfone: ${event.error}`,
        "error",
      );

      if (event.error === "network") {
        recognition.abort();
        window.setTimeout(() => {
          listenWithBackend("network");
        }, 200);
      }
    };
    recognition.onresult = async (event) => {
      const transcript = event.results[0][0].transcript;
      setInput(transcript);
      await submitCommand(transcript.trim());
    };

    try {
      recognition.start();
    } catch {
      setIsListening(false);
      addMessage("jarvis", "Nao consegui iniciar a escuta do microfone.", "error");
    }
  }

  return (
    <div className="relative min-h-screen overflow-hidden bg-[#030b14] font-sans text-cyan-100">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(0,180,255,0.08),transparent_45%)]" />
      <div className="absolute inset-0 bg-[linear-gradient(rgba(0,255,255,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(0,255,255,0.03)_1px,transparent_1px)] bg-[size:50px_50px] opacity-20" />

      <header className="relative z-10 flex h-16 items-center justify-between border-b border-cyan-500/20 bg-[#07111c]/70 px-6 shadow-[0_0_25px_rgba(0,255,255,0.08)] backdrop-blur-xl">
        <div className="flex items-center gap-4">
          <h1 className="text-2xl font-bold tracking-[0.35em] text-cyan-300 drop-shadow-[0_0_10px_rgba(0,255,255,0.8)]">
            J.A.R.V.I.S
          </h1>

          <div
            className={[
              "flex items-center gap-2 rounded-full border px-3 py-1",
              apiOnline
                ? "border-emerald-400/30 bg-emerald-500/10"
                : "border-red-400/30 bg-red-500/10",
            ].join(" ")}
          >
            <div
              className={[
                "h-2 w-2 animate-pulse rounded-full",
                apiOnline ? "bg-emerald-400" : "bg-red-400",
              ].join(" ")}
            />
            <span
              className={[
                "text-xs tracking-wider",
                apiOnline ? "text-emerald-300" : "text-red-200",
              ].join(" ")}
            >
              {apiOnline ? "API Online" : "API Offline"}
            </span>
          </div>
        </div>

        <div className="flex items-center gap-5 rounded-xl border border-cyan-500/20 bg-[#081420]/80 px-6 py-2 shadow-[0_0_20px_rgba(0,180,255,0.1)] backdrop-blur-md">
          <span className="text-sm tracking-[0.2em] text-cyan-300">
            {new Date().toLocaleTimeString("pt-BR")}
          </span>
          <div className="h-5 w-px bg-cyan-500/20" />
          <span className="text-sm text-cyan-100/80">
            {new Date().toLocaleDateString("pt-BR")}
          </span>
        </div>

        <div className="flex items-center gap-4">
          <div className="hidden text-right lg:block">
            <div className="text-xs uppercase tracking-[0.18em] text-cyan-500/70">
              Usuario
            </div>
            <div className="max-w-[150px] truncate text-sm text-cyan-100">
              {currentUser?.name ?? "Operador"}
            </div>
          </div>

          <button
            className="rounded-xl border border-cyan-500/20 bg-[#081420]/80 px-4 py-2 text-sm shadow-[0_0_20px_rgba(0,180,255,0.08)] transition-all hover:border-cyan-400/50"
            onClick={onLogout}
            type="button"
          >
            Sair
          </button>
        </div>
      </header>

      <div className="relative z-10 flex h-[calc(100vh-64px)]">
        <aside className="flex w-[290px] flex-col gap-4 overflow-y-auto border-r border-cyan-500/10 bg-[#05101b]/40 p-4 backdrop-blur-lg">
          <GlassCard title="Conexao">
            <div className="space-y-4">
              <MiniStat label="Backend" value={apiOnline ? "Online" : "Offline"} />
              <MiniStat label="Voz" value={voiceEnabled ? "Ativa" : "Muda"} />
              <MiniStat label="Camera" value={cameraEnabled ? "Ativa" : "Off"} />

              <button
                className="w-full rounded-xl border border-cyan-500/20 bg-cyan-500/5 px-4 py-3 text-sm transition hover:bg-cyan-500/10"
                onClick={checkStatus}
                type="button"
              >
                Verificar API
              </button>
            </div>
          </GlassCard>

          <GlassCard title="Memoria">
            <div className="space-y-3 text-sm leading-6 text-cyan-100/70">
              <p>Diga ou digite: meu nome e Ana.</p>
              <p>Depois pergunte: qual meu nome?</p>
            </div>
          </GlassCard>

          <GlassCard title="Comandos">
            <div className="grid gap-2">
              {["abrir youtube", "abrir google", "abrir calculadora"].map(
                (command) => (
                  <button
                    className="rounded-xl border border-cyan-500/15 bg-[#020812]/70 px-3 py-3 text-left text-sm text-cyan-100/80 transition hover:border-cyan-400/40 hover:text-cyan-50"
                    key={command}
                    onClick={() => setInput(command)}
                    type="button"
                  >
                    {command}
                  </button>
                ),
              )}
            </div>
          </GlassCard>
        </aside>

        <main className="relative flex flex-1 items-center justify-center overflow-hidden">
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(0,180,255,0.05),transparent_60%)]" />

          <div className="flex flex-col items-center">
            <div className="relative flex h-[420px] w-[420px] items-center justify-center">
              <div className="absolute inset-0 animate-pulse rounded-full border border-cyan-500/10" />
              <div className="absolute h-[380px] w-[380px] animate-spin rounded-full border border-cyan-500/20 [animation-duration:20s]" />
              <div className="absolute h-[320px] w-[320px] animate-spin rounded-full border border-cyan-400/30 [animation-direction:reverse] [animation-duration:14s]" />
              <div className="absolute h-[250px] w-[250px] animate-pulse rounded-full border border-cyan-300/20" />
              <div className="absolute h-[180px] w-[180px] rounded-full border border-cyan-400/20 bg-cyan-400/5 shadow-[0_0_80px_rgba(0,255,255,0.4)]" />

              <div className="absolute flex h-[120px] w-[120px] items-center justify-center rounded-full border border-cyan-300/40 bg-cyan-400/10 shadow-[0_0_50px_rgba(0,255,255,0.8)]">
                <div className="flex gap-2">
                  <span className="h-6 w-2 animate-pulse rounded-full bg-cyan-300" />
                  <span className="h-6 w-2 animate-pulse rounded-full bg-cyan-300 delay-75" />
                  <span className="h-6 w-2 animate-pulse rounded-full bg-cyan-300 delay-150" />
                  <span className="h-6 w-2 animate-pulse rounded-full bg-cyan-300 delay-300" />
                  <span className="h-6 w-2 animate-pulse rounded-full bg-cyan-300 delay-500" />
                </div>
              </div>
            </div>

            <h2 className="mt-8 text-5xl font-bold tracking-[0.35em] text-cyan-100 drop-shadow-[0_0_20px_rgba(0,255,255,0.5)]">
              J.A.R.V.I.S
            </h2>

            <div className="mt-4 flex items-center gap-3 rounded-full border border-cyan-500/20 bg-cyan-500/5 px-6 py-2 shadow-[0_0_20px_rgba(0,255,255,0.08)] backdrop-blur-xl">
              <div className="h-2 w-2 animate-pulse rounded-full bg-emerald-400" />
              <span className="text-sm tracking-wide text-cyan-300">
                {isSending ? "Processando comando..." : "Aguardando comando..."}
              </span>
            </div>

            <div className="mt-24 flex items-center gap-8">
              <ActionButton
                active={cameraEnabled}
                label="CAM"
                onClick={() => setCameraEnabled((current) => !current)}
              />
              <ActionButton
                active={isListening}
                disabled={!browserCanListen && !apiOnline}
                label="MIC"
                onClick={startBrowserListening}
              />
              <ActionButton
                active={voiceEnabled}
                label="VOZ"
                onClick={() => setVoiceEnabled((current) => !current)}
              />
            </div>
          </div>
        </main>

        <aside className="flex w-[380px] flex-col border-l border-cyan-500/10 bg-[#05101b]/40 p-4 backdrop-blur-lg">
          <div className="mb-4 flex items-center justify-between">
            <h3 className="text-lg tracking-wide text-cyan-200">Conversa</h3>

            <div className="flex gap-2">
              <button
                className="rounded-lg border border-cyan-500/20 bg-cyan-500/5 px-3 py-1 text-xs transition-all hover:bg-cyan-500/10"
                onClick={clearMessages}
                type="button"
              >
                Limpar
              </button>

              <button
                className="rounded-lg border border-cyan-500/20 bg-cyan-500/5 px-3 py-1 text-xs transition-all hover:bg-cyan-500/10"
                onClick={exportConversation}
                type="button"
              >
                Exportar
              </button>
            </div>
          </div>

          <div
            className="flex-1 overflow-y-auto rounded-2xl border border-cyan-500/10 bg-[#07111c]/60 p-4 shadow-inner shadow-cyan-500/5"
            ref={messagesRef}
          >
            <div className="space-y-3">
              {messages.map((message) => (
                <MessageBubble key={message.id} message={message} />
              ))}
            </div>
          </div>

          <form className="mt-4 flex gap-2" onSubmit={sendMessage}>
            <input
              className="flex-1 rounded-xl border border-cyan-500/10 bg-[#07111c]/80 px-4 py-3 text-sm outline-none transition-all placeholder:text-cyan-500/40 focus:border-cyan-400/40"
              onChange={(event) => setInput(event.target.value)}
              placeholder="Digite um comando..."
              ref={inputRef}
              type="text"
              value={input}
            />

            <button
              className="w-24 rounded-xl border border-cyan-400/20 bg-cyan-500/10 text-sm font-semibold text-cyan-200 shadow-[0_0_20px_rgba(0,255,255,0.2)] transition-all hover:bg-cyan-500/20 disabled:opacity-50"
              disabled={isSending}
              type="submit"
            >
              Enviar
            </button>
          </form>
        </aside>
      </div>
    </div>
  );
}

function MessageBubble({ message }) {
  const isUser = message.role === "user";

  return (
    <div className={["flex", isUser ? "justify-end" : "justify-start"].join(" ")}>
      <div
        className={[
          "max-w-[90%] rounded-2xl border p-4 shadow-[0_0_20px_rgba(0,255,255,0.08)] backdrop-blur-md",
          isUser
            ? "border-cyan-300/20 bg-cyan-300/10"
            : "border-cyan-500/10 bg-cyan-500/5",
        ].join(" ")}
      >
        <p className="text-sm leading-relaxed text-cyan-100/90">{message.text}</p>
        <span className="mt-3 block text-[10px] uppercase tracking-[0.16em] text-cyan-400/40">
          {message.source} - {formatTime(message.time)}
        </span>
      </div>
    </div>
  );
}

function GlassCard({ title, children }) {
  return (
    <div className="relative overflow-hidden rounded-2xl border border-cyan-500/10 bg-[#08131d]/60 p-4 shadow-[0_0_25px_rgba(0,255,255,0.05)] backdrop-blur-xl">
      <div className="absolute inset-0 bg-[linear-gradient(180deg,rgba(0,255,255,0.03),transparent)]" />

      <div className="relative z-10">
        <div className="mb-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="h-2 w-2 rounded-full bg-cyan-400" />
            <h3 className="text-sm uppercase tracking-widest text-cyan-200">
              {title}
            </h3>
          </div>
        </div>

        {children}
      </div>
    </div>
  );
}

function MiniStat({ label, value }) {
  return (
    <div className="rounded-xl border border-cyan-500/10 bg-[#020812]/70 px-3 py-4 text-center shadow-inner shadow-cyan-500/5">
      <div className="text-[10px] uppercase tracking-[0.2em] text-cyan-500/60">
        {label}
      </div>
      <div className="mt-2 text-sm text-cyan-200">{value}</div>
    </div>
  );
}

function ActionButton({ active, disabled = false, label, onClick }) {
  return (
    <button
      className={[
        "flex h-16 w-16 items-center justify-center rounded-2xl border text-sm font-semibold shadow-[0_0_25px_rgba(0,255,255,0.12)] backdrop-blur-xl transition-all duration-300 hover:scale-110 disabled:cursor-not-allowed disabled:opacity-40",
        active
          ? "border-emerald-300/50 bg-emerald-400/15 text-emerald-100"
          : "border-cyan-500/20 bg-[#08131d]/80 text-cyan-200 hover:border-cyan-300/50",
      ].join(" ")}
      disabled={disabled}
      onClick={onClick}
      type="button"
    >
      {label}
    </button>
  );
}

function getSpeechRecognition() {
  if (typeof window === "undefined") {
    return null;
  }

  return window.SpeechRecognition || window.webkitSpeechRecognition || null;
}

function formatTime(date) {
  return new Intl.DateTimeFormat("pt-BR", {
    hour: "2-digit",
    minute: "2-digit",
  }).format(date);
}
