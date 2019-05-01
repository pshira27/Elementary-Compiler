import argparse
import bcclex
import bccparse
import codeGen
import subprocess
import platform

system_platform = platform.system()

# parser = argparse.ArgumentParser(description='Bcc compiler')
# parser.add_argument("input", help="Path of file to compile.")
# parser.add_argument("output_asm", help="Output assembly file name.")
# parser.add_argument("output_exec", help="Output executeable file name.")
# args = parser.parse_args()


lines = open("test.bcc", 'r').read()
codeGen.lexer = bcclex.lexer
result = bccparse.parse(lines)
codeGen.statement_main(result)

print("\n----- ASM simple -----")
print(codeGen.getHeader())
print(codeGen.getData())
print(codeGen.getText())



# if result:
#     util.statement_main(result)
#     file = open(args.output_asm, 'w')
#     file.writelines(util.asmheader)
#     file.writelines(util.asmdata)
#     file.writelines(util.asmtext)
#     file.writelines(util.asmleave)
#     file.close()

#     if system_platform not in nasm_args:
#         print("Compile to executeable for this platform is not supported yet.")
#     else:
#         nasm_arg = nasm_args[system_platform]
#         p = subprocess.Popen(['nasm', '-f', nasm_arg, args.output_asm, '-o', args.output_asm[:-3] + 'o'])
#         p.wait()
#         p = subprocess.Popen(
#             ['gcc', '-w', '-no-pie', '-m64', '-o', args.output_exec, args.output_asm[:-3] + 'o'])
#         p.wait()
#         print("Compiled successfully.")
