@echo off
nasm -f win64 test.asm -o test.o
gcc test.o -o test.exe
cmd /k