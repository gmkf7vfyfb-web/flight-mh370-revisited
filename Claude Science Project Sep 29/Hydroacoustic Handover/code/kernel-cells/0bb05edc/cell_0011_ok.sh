cd /Users/pete/Downloads; f='art%3A10.1007%2Fs00024-022-03117-6.pdf'; ls -la "$f"; shasum -a 256 "$f" | cut -c1-16
python - <<'EOF'
import pypdf
r=pypdf.PdfReader('/Users/pete/Downloads/art%3A10.1007%2Fs00024-022-03117-6.pdf')
print(len(r.pages)); t=r.pages[0].extract_text(); print(t[:700])
EOF