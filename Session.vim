let SessionLoad = 1
let s:so_save = &g:so | let s:siso_save = &g:siso | setg so=0 siso=0 | setl so=-1 siso=-1
let v:this_session=expand("<sfile>:p")
silent only
silent tabonly
cd ~/codin/cso_assignments/CSE392/lora-mesh/LmicMesher/logs/network-simulator/network-simulator-py
if expand('%') == '' && !&modified && line('$') <= 1 && getline(1) == ''
  let s:wipebuf = bufnr('%')
endif
let s:shortmess_save = &shortmess
if &shortmess =~ 'A'
  set shortmess=aoOA
else
  set shortmess=aoO
endif
badd +80 app.py
badd +93 ~/.local/lib/python3.10/site-packages/flask_socketio/__init__.py
badd +10 src/main.py
badd +76 templates/index.html
badd +7 ~/codin/cso_assignments/CSE392/lora-mesh/LmicMesher/logs/network-simulator/network-simulator-py/src/utils.py
badd +26 ~/codin/cso_assignments/CSE392/lora-mesh/LmicMesher/logs/network-simulator/network-simulator-py/src/node.py
argglobal
%argdel
$argadd app.py
edit templates/index.html
let s:save_splitbelow = &splitbelow
let s:save_splitright = &splitright
set splitbelow splitright
wincmd _ | wincmd |
vsplit
1wincmd h
wincmd w
let &splitbelow = s:save_splitbelow
let &splitright = s:save_splitright
wincmd t
let s:save_winminheight = &winminheight
let s:save_winminwidth = &winminwidth
set winminheight=0
set winheight=1
set winminwidth=0
set winwidth=1
exe 'vert 1resize ' . ((&columns * 106 + 106) / 213)
exe 'vert 2resize ' . ((&columns * 106 + 106) / 213)
argglobal
balt app.py
setlocal foldmethod=manual
setlocal foldexpr=0
setlocal foldmarker={{{,}}}
setlocal foldignore=#
setlocal foldlevel=0
setlocal foldminlines=1
setlocal foldnestmax=20
setlocal foldenable
silent! normal! zE
let &fdl = &fdl
let s:l = 78 - ((12 * winheight(0) + 12) / 24)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 78
normal! 025|
wincmd w
argglobal
if bufexists(fnamemodify("~/codin/cso_assignments/CSE392/lora-mesh/LmicMesher/logs/network-simulator/network-simulator-py/src/node.py", ":p")) | buffer ~/codin/cso_assignments/CSE392/lora-mesh/LmicMesher/logs/network-simulator/network-simulator-py/src/node.py | else | edit ~/codin/cso_assignments/CSE392/lora-mesh/LmicMesher/logs/network-simulator/network-simulator-py/src/node.py | endif
if &buftype ==# 'terminal'
  silent file ~/codin/cso_assignments/CSE392/lora-mesh/LmicMesher/logs/network-simulator/network-simulator-py/src/node.py
endif
balt ~/codin/cso_assignments/CSE392/lora-mesh/LmicMesher/logs/network-simulator/network-simulator-py/src/utils.py
setlocal foldmethod=manual
setlocal foldexpr=0
setlocal foldmarker={{{,}}}
setlocal foldignore=#
setlocal foldlevel=0
setlocal foldminlines=1
setlocal foldnestmax=20
setlocal foldenable
silent! normal! zE
let &fdl = &fdl
let s:l = 35 - ((10 * winheight(0) + 12) / 24)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 35
normal! 0
wincmd w
exe 'vert 1resize ' . ((&columns * 106 + 106) / 213)
exe 'vert 2resize ' . ((&columns * 106 + 106) / 213)
tabnext 1
if exists('s:wipebuf') && len(win_findbuf(s:wipebuf)) == 0 && getbufvar(s:wipebuf, '&buftype') isnot# 'terminal'
  silent exe 'bwipe ' . s:wipebuf
endif
unlet! s:wipebuf
set winheight=1 winwidth=20
let &shortmess = s:shortmess_save
let &winminheight = s:save_winminheight
let &winminwidth = s:save_winminwidth
let s:sx = expand("<sfile>:p:r")."x.vim"
if filereadable(s:sx)
  exe "source " . fnameescape(s:sx)
endif
let &g:so = s:so_save | let &g:siso = s:siso_save
set hlsearch
nohlsearch
doautoall SessionLoadPost
unlet SessionLoad
" vim: set ft=vim :
