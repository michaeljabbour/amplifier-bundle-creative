---
bundle:
  name: creative
  version: 0.1.0
  description: Multi-modal creative production — image → video → audio → cut

includes:
  - bundle: git+https://github.com/microsoft/amplifier-foundation@main
  - bundle: git+https://github.com/microsoft/amplifier-bundle-recipes@main
  - bundle: creative:behaviors/full-production

spawn:
  exclude_tools: [tool-task]
---

# Creative Production System

@creative:context/creative-instructions.md

---

@foundation:context/shared/common-system-base.md
