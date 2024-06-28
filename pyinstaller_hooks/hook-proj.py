# import sys
# import os
# from PyInstaller.utils.hooks import collect_submodules
# from PyInstaller.compat import is_win,is_darwin
# # hiddenimports = ['proj']
# if hasattr(sys, 'real_prefix'):  # check if in a virtual environment
#     root_path = sys.real_prefix
# else:
#     root_path = sys.prefix
# # - conda-specific
# if is_win:
#     tgt_proj_data = os.path.join('Library', 'share', 'proj')
#     src_proj_data = os.path.join(root_path, 'Library', 'share', 'proj')
# else:  # both linux and darwin
#     tgt_proj_data = os.path.join('share', 'proj')
#     src_proj_data = os.path.join(root_path, 'share', 'proj')
# print(src_proj_data,'--->',tgt_proj_data)
# datas = []
# if os.path.exists(src_proj_data):
#     datas.append((src_proj_data, tgt_proj_data))