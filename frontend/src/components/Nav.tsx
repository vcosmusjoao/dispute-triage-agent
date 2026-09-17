import Link from "next/link";

export default function Nav() {
  return (
    <nav className="flex items-center gap-6 border-b border-text/20 pb-4">
      <Link href="/" className="font-fira-code text-highlight">
        Dispute Triage Agent
      </Link>
      <div className="flex gap-4 font-fira-code text-sm">
        <Link href="/" className="text-text/60 hover:text-highlight">
          Demo
        </Link>
        <Link href="/how-it-works" className="text-text/60 hover:text-highlight">
          How it works
        </Link>
      </div>
    </nav>
  );
}
