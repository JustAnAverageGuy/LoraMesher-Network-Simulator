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
badd +10 main.py
badd +5 src/constants.py
badd +34 src//node.py
badd +7 interval.py
badd +14 ~/codin/cso_assignments/CSE392/lora-mesh/LmicMesher/logs/network-simulator/network-simulator-py/src/interval.py
badd +214 ~/.local/share/nvim/mason/packages/basedpyright/venv/lib/python3.10/site-packages/basedpyright/dist/typeshed-fallback/stdlib/math.pyi
badd +55 src/packet.py
badd +31 ~/codin/cso_assignments/CSE392/lora-mesh/LmicMesher/logs/network-simulator/network-simulator-ts/src/types.ts
badd +1377 /usr/lib/python3.10/threading.py
badd +20 src/html_template.py
argglobal
%argdel
$argadd main.py
set stal=2
tabnew +setlocal\ bufhidden=wipe
tabrewind
edit src/constants.py
let s:save_splitbelow = &splitbelow
let s:save_splitright = &splitright
set splitbelow splitright
wincmd _ | wincmd |
split
1wincmd k
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
exe '1resize ' . ((&lines * 24 + 26) / 52)
exe '2resize ' . ((&lines * 24 + 26) / 52)
argglobal
balt main.py
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
let s:l = 18 - ((17 * winheight(0) + 12) / 24)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 18
normal! 015|
wincmd w
argglobal
if bufexists(fnamemodify("main.py", ":p")) | buffer main.py | else | edit main.py | endif
if &buftype ==# 'terminal'
  silent file main.py
endif
balt src/constants.py
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
let s:l = 10 - ((9 * winheight(0) + 12) / 24)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 10
normal! 086|
wincmd w
exe '1resize ' . ((&lines * 24 + 26) / 52)
exe '2resize ' . ((&lines * 24 + 26) / 52)
tabnext
edit src/html_template.py
argglobal
balt src/constants.py
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
let s:l = 34 - ((33 * winheight(0) + 24) / 49)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 34
normal! 034|
tabnext 1
set stal=1
if exists('s:wipebuf') && len(win_findbuf(s:wipebuf)) == 0 && getbufvar(s:wipebuf, '&buftype') isnot# 'terminal'
  silent exe 'bwipe ' . s:wipebuf
endif
unlet! s:wipebuf
set winheight=1 winwidth=20
let &shortmess = s:shortmess_save
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
