export default function AlertMessage({ message }) {
  if (!message) return null;

  return (
    <div
      className={`p-4 mb-6 rounded-lg text-sm whitespace-pre-wrap ${
        message.type === "success"
          ? "bg-emerald-50 text-emerald-700 border border-emerald-200"
          : "bg-rose-50 text-rose-700 border border-rose-200"
      }`}
    >
      {message.text}
    </div>
  );
}
