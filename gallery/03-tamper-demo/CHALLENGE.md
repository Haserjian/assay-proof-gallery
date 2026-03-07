# Assay Challenge Pack

Two proof packs. One is authentic. One has been tampered with.
Your machine decides which is real.

```bash
python3 -m pip install assay-ai
assay verify-pack ./good/
assay verify-pack ./tampered/
```

One will exit 0 (authentic). One will exit non-zero (tampered).

To see the full explanation:
```bash
assay explain ./good/
assay explain ./tampered/
```

Learn more: https://github.com/Haserjian/assay
