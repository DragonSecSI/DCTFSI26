# $ cmp -l dragon dragon_patched
# 351248  17 220
# 351249 204 220
# 351250 237 220
# 351251   1 220
# 351252   0 220
# 351253   0 220

import shutil
shutil.copy("dragon", "dragon_patched")

with open("dragon_patched", "r+b") as f:
    f.seek(351248-1)
    f.write(bytes([0o220]*6)) 


