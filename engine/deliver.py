#!/usr/bin/env python3
"""Send the daily news email via Gmail SMTP. Standard library only.

The Gmail App Password is read from an environment variable (never stored in the
repo). Generate one at https://myaccount.google.com/apppasswords and export it:

    export NEWS_AGENT_GMAIL_APP_PW="xxxx xxxx xxxx xxxx"

Usage:
    python deliver.py --to you@gmail.com --from you@gmail.com \
        --subject "Daily Stock News — Jun 7, 2026" --body path/to/email.md
    # add --dry-run to print the message instead of sending
"""
import argparse
import os
import smtplib
import ssl
import sys
from email.message import EmailMessage

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 465  # SSL


def md_to_basic_html(md: str) -> str:
    """Minimal markdown -> HTML so the email renders nicely. No dependencies."""
    import html as _html

    lines, out, in_ul = md.splitlines(), [], False
    for raw in lines:
        line = _html.escape(raw.rstrip())
        if line.startswith("### "):
            if in_ul: out.append("</ul>"); in_ul = False
            out.append(f"<h3>{line[4:]}</h3>")
        elif line.startswith("## "):
            if in_ul: out.append("</ul>"); in_ul = False
            out.append(f"<h2>{line[3:]}</h2>")
        elif line.startswith("# "):
            if in_ul: out.append("</ul>"); in_ul = False
            out.append(f"<h1>{line[2:]}</h1>")
        elif line.lstrip().startswith(("- ", "* ")):
            if not in_ul: out.append("<ul>"); in_ul = True
            out.append(f"<li>{line.lstrip()[2:]}</li>")
        elif not line.strip():
            if in_ul: out.append("</ul>"); in_ul = False
            out.append("<br>")
        else:
            if in_ul: out.append("</ul>"); in_ul = False
            out.append(f"<p>{line}</p>")
    if in_ul: out.append("</ul>")
    body = "\n".join(out)
    return (f'<div style="font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif;'
            f'font-size:14px;line-height:1.45;max-width:680px">{body}</div>')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--to", required=True)
    ap.add_argument("--from", dest="sender", required=True)
    ap.add_argument("--subject", required=True)
    ap.add_argument("--body", required=True, help="path to markdown body file")
    ap.add_argument("--pw-env", default="NEWS_AGENT_GMAIL_APP_PW")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    with open(args.body, encoding="utf-8") as f:
        md = f.read()

    msg = EmailMessage()
    msg["From"], msg["To"], msg["Subject"] = args.sender, args.to, args.subject
    msg.set_content(md)  # plain-text fallback
    msg.add_alternative(md_to_basic_html(md), subtype="html")

    if args.dry_run:
        print(f"[dry-run] To: {args.to}\nSubject: {args.subject}\n\n{md}")
        return

    pw = os.environ.get(args.pw_env)
    if not pw:
        sys.exit(f"ERROR: env var {args.pw_env} not set (Gmail App Password).")

    ctx = ssl.create_default_context()
    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=ctx) as s:
        s.login(args.sender, pw)
        s.send_message(msg)
    print(f"Sent to {args.to}: {args.subject!r}")


if __name__ == "__main__":
    main()
