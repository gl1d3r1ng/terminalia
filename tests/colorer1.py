import re
import blessed

term = blessed.Terminal()

msg1 = r"[tomato]red[normal] \[text\]"
msg0 = r"I am a \[purple\] [on_mediumpurple4]T[on_mediumpurple3]E[on_mediumpurple2]X[on_mediumpurple1]T[normal]"

#print(re.findall(r"(?<!\\)\[.*?]", msg1))
for msg in [msg0, msg1]:
    matchs = re.findall(r"(?<!\\)\[.*?]", msg)
    for match in matchs:
        msg = msg.replace(match, f"{getattr(term, match[1:-1])}")
    msg = msg.replace(r"\[", "[").replace(r"\]", "]")
    print(msg)

