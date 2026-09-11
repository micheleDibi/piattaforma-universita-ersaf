export default function AlertMessage({ message }) {
  if (!message) return null;

  return (
    <div
      className={`p-4 mb-6 rounded-controllo text-sm whitespace-pre-wrap ${
        message.type === "success"
          ? "bg-positivo/10 text-positivo border border-positivo/20"
          : "bg-negativo-tenue text-negativo border border-negativo/20"
      }`}
    >
      {message.text}
    </div>
  );
}
