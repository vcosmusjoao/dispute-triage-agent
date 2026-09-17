import Link from "next/link";

export default function Nav() {
  return (
    <nav className="border-b border-neutral-200 dark:border-neutral-800">
      <div className="mx-auto flex max-w-5xl items-center gap-6 px-6 py-4">
        <Link href="/" className="font-semibold text-neutral-900 dark:text-neutral-100">
          Dispute Triage Agent
        </Link>
        <div className="flex gap-4 text-sm">
          <Link
            href="/"
            className="text-neutral-500 hover:text-violet-600 dark:text-neutral-400 dark:hover:text-violet-400"
          >
            Demo
          </Link>
          <Link
            href="/how-it-works"
            className="text-neutral-500 hover:text-violet-600 dark:text-neutral-400 dark:hover:text-violet-400"
          >
            How it works
          </Link>
        </div>
      </div>
    </nav>
  );
}
