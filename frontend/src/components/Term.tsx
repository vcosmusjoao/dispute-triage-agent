"use client";

import { useRef, useState } from "react";

const TOOLTIP_WIDTH = 224; // px, matches the w-56 box below
const VIEWPORT_MARGIN = 8; // px, keeps the tooltip off the screen edge

export default function Term({
  children,
  definition,
}: {
  children: string;
  definition: string;
}) {
  const [open, setOpen] = useState(false);
  const [position, setPosition] = useState({ left: 0, top: 0 });
  const buttonRef = useRef<HTMLButtonElement>(null);

  function show() {
    const rect = buttonRef.current?.getBoundingClientRect();
    if (rect) {
      // Anchor above the term (rect.top), then clamp horizontally so the
      // box never runs past either edge of the viewport - the term can
      // sit anywhere on the page, near the left margin or the last word
      // on a line.
      const left = Math.min(
        Math.max(rect.left, VIEWPORT_MARGIN),
        window.innerWidth - TOOLTIP_WIDTH - VIEWPORT_MARGIN
      );
      setPosition({ left, top: rect.top - 8 });
    }
    setOpen(true);
  }

  return (
    <span>
      <button
        ref={buttonRef}
        type="button"
        onClick={() => (open ? setOpen(false) : show())}
        onMouseEnter={show}
        onMouseLeave={() => setOpen(false)}
        onBlur={() => setOpen(false)}
        aria-expanded={open}
        className="cursor-help border-b border-dotted border-violet-400 font-medium text-violet-700 hover:border-violet-600 hover:text-violet-800 dark:border-violet-600 dark:text-violet-300 dark:hover:border-violet-400 dark:hover:text-violet-200"
      >
        {children}
      </button>
      {open && (
        <span
          role="tooltip"
          style={{ left: position.left, top: position.top }}
          className="fixed z-10 w-56 -translate-y-full rounded-md border border-violet-200 bg-white p-2 text-xs font-normal text-neutral-700 shadow-lg dark:border-violet-900 dark:bg-neutral-900 dark:text-neutral-300"
        >
          {definition}
        </span>
      )}
    </span>
  );
}
