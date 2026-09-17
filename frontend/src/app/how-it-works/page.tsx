import type { Metadata } from "next";
import Link from "next/link";
import PipelineDiagram from "@/components/PipelineDiagram";
import Term from "@/components/Term";

export const metadata: Metadata = {
  title: "How it works | Dispute Triage Agent",
  description: "What a chargeback dispute is, what this agent decides, and why it needs an LLM instead of a rules engine.",
};

export default function HowItWorks() {
  return (
    <main className="max-w-3xl py-8">
      <header className="mb-10">
        <h1 className="text-2xl">How it works</h1>
        <p className="mt-1 text-sm text-text/60">
          The domain, the decision, and why it&apos;s an agent instead of an if/else chain.
        </p>
      </header>

      <div className="flex flex-col gap-10">
        <section>
          <h2 className="text-lg">What&apos;s a chargeback</h2>
          <p className="mt-2 text-sm leading-relaxed text-text/80">
            A{" "}
            <Term definition="The person who owns the card and made the original purchase.">
              cardholder
            </Term>{" "}
            disputes a charge with their bank, the{" "}
            <Term definition="The cardholder's bank: the one that issued their card, and the one that decides the dispute.">
              issuer
            </Term>
            . The issuer reverses the money from the merchant immediately: a provisional credit
            to the cardholder, taken as fact until proven otherwise. Only after that reversal does
            the merchant get a chance to argue back. It&apos;s guilty-until-proven-innocent from
            the merchant&apos;s side, which is the entire reason the rest of this process exists.
          </p>
        </section>

        <section>
          <h2 className="text-lg">
            Why the{" "}
            <Term definition="The card network's classification for why the dispute was filed, e.g. fraud or item not received. Set by the issuer, interpreted by the merchant.">
              reason code
            </Term>{" "}
            matters
          </h2>
          <p className="mt-2 text-sm leading-relaxed text-text/80">
            Every dispute carries a card-network reason code: &quot;product not received,&quot;
            &quot;fraud, card-not-present,&quot; &quot;cancelled service,&quot; and dozens more.
            The code isn&apos;t bureaucratic labeling, it determines what evidence actually
            matters. Proof of delivery wins a not-received claim but is irrelevant to a fraud
            claim, where{" "}
            <Term definition="Address Verification Service: checks whether the billing address given at checkout matches the one on file with the card issuer.">
              AVS
            </Term>
            /
            <Term definition="Card Verification Value: the 3-4 digit security code on the card, checked to prove the buyer physically had it.">
              CVV
            </Term>
            /
            <Term definition="3-D Secure (branded as Verified by Visa or Mastercard SecureCode): an extra checkout authentication step, like a one-time password, that shifts fraud liability onto the issuer when used.">
              3DS
            </Term>{" "}
            authentication signals matter instead. That&apos;s why <code>classify</code>,
            interpreting the code before any judgment happens, is the agent&apos;s first step,
            not an afterthought.
          </p>
        </section>

        <section>
          <h2 className="text-lg">
            Fight or accept:{" "}
            <Term definition="The merchant's formal written rebuttal, submitted with evidence, arguing the charge was legitimate.">
              representment
            </Term>
          </h2>
          <p className="mt-2 text-sm leading-relaxed text-text/80">
            To fight a chargeback, the merchant submits a formal written rebuttal, a
            representment letter, with documented evidence that the charge was legitimate. That
            takes real effort, and fighting isn&apos;t free even when you have a case: card
            networks track how often merchants dispute and lose, and fighting too often on weak
            evidence has its own cost. So the actual decision is a judgment call, weighing the
            odds of winning against the cost of trying, not just &quot;do we have the textbook
            evidence or not.&quot;
          </p>
        </section>

        <section>
          <h2 className="text-lg">The pipeline</h2>
          <p className="mt-2 mb-4 text-sm leading-relaxed text-text/80">
            One dispute flows through four steps, each one handing the next a little more of the
            final verdict:
          </p>
          <PipelineDiagram />
        </section>

        <section>
          <h2 className="text-lg">Why an LLM, not a rules engine</h2>
          <p className="mt-2 text-sm leading-relaxed text-text/80">
            A rules engine handles the easy cases fine: AVS mismatch plus a foreign IP is almost
            always a loss, clean history plus solid delivery proof is almost always a win. The
            hard cases are the ones where signals point in different directions: a 4-year
            customer with zero prior chargebacks, but no tracking number for this one order.
            Rules force a threshold on that; an LLM can weigh the signals against each other and
            explain <em>why</em>, in plain English, the way an experienced analyst actually
            would. That reasoning step, not the drafting, is where this agent earns its keep over
            a spreadsheet of if/else rules.
          </p>
        </section>

        <Link
          href="/"
          className="self-start rounded-md border border-highlight bg-highlight/10 px-5 py-2.5 font-fira-code font-medium text-highlight transition hover:bg-highlight/20"
        >
          Try the demo →
        </Link>
      </div>
    </main>
  );
}
