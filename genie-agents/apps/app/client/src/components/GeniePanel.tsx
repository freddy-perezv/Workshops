import { Bot, Sparkles } from 'lucide-react';
import { GenieChat } from '@databricks/appkit-ui/react';

interface GeniePanelProps {
  mockMode: boolean;
}

const prompts = [
  '¿Qué explica las señales críticas?',
  '¿Qué decisiones se tomaron hoy?',
  '¿Qué contribuyentes requieren revisión?',
];

export function GeniePanel({ mockMode }: GeniePanelProps) {
  return (
    <section className="panel genie-panel">
      <div className="panel__header genie-panel__header">
        <div className="genie-avatar">
          <Sparkles size={18} />
        </div>
        <div>
          <p className="eyebrow">Genie Agent</p>
          <h2>Copiloto de riesgo tributario</h2>
        </div>
        <span className="online-badge">En línea</span>
      </div>

      {mockMode ? (
        <div className="mock-chat">
          <div className="mock-chat__message mock-chat__message--agent">
            <Bot size={17} />
            <p>
              Encontré <strong>18 contribuyentes de riesgo alto</strong>. La
              mayor exposición priorizada está en Lima, impulsada por brechas
              entre ventas declaradas e información de terceros.
            </p>
          </div>
          <div className="mock-chat__context">
            <span>Preguntas sugeridas</span>
            {prompts.map((prompt) => (
              <button key={prompt}>{prompt}</button>
            ))}
          </div>
          <div className="mock-chat__composer">
            <input
              aria-label="Pregunta para Genie"
              placeholder="Pregunta sobre ventas, riesgo o decisiones…"
              disabled
            />
            <button disabled>Enviar</button>
          </div>
          <small className="mock-notice">
            Vista local. Genie se activa al asociar el recurso en Databricks.
          </small>
        </div>
      ) : (
        <div className="genie-chat-host">
          <GenieChat alias="radar-tributario" />
        </div>
      )}
    </section>
  );
}
