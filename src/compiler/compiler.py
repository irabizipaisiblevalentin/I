"""
Main compiler for the I programming language.

This module ties together all compiler components into a unified compiler.
"""

import sys
import argparse
from pathlib import Path
from typing import Optional

from compiler.lexer.lexer import Lexer, LexerError
from compiler.parser.parser import Parser, ParseError
from compiler.semantic.analyzer import SemanticAnalyzer
from compiler.semantic.errors import SemanticErrorCollection
from compiler.codegen.generator import CodeGenerator
from compiler.codegen.bytecode import Chunk
from vm.virtual_machine import VirtualMachine, RuntimeError as VMRuntimeError


class Compiler:
    """Main compiler for the I programming language."""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.lexer = None
        self.parser = None
        self.semantic_analyzer = None
        self.code_generator = None
        self.vm = None
    
    def compile_file(self, file_path: str) -> Chunk:
        """
        Compile a file and return the bytecode chunk.
        
        Args:
            file_path: Path to the source file
            
        Returns:
            Compiled bytecode chunk
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            LexerError: If there's a lexical error
            ParseError: If there's a parse error
            SemanticError: If there's a semantic error
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        source = path.read_text(encoding='utf-8')
        return self.compile_source(source, path.stem)
    
    def compile_source(self, source: str, chunk_name: str = "main") -> Chunk:
        """
        Compile source code and return the bytecode chunk.
        
        Args:
            source: Source code to compile
            chunk_name: Name for the bytecode chunk
            
        Returns:
            Compiled bytecode chunk
            
        Raises:
            LexerError: If there's a lexical error
            ParseError: If there's a parse error
            SemanticError: If there's a semantic error
        """
        # Lexical Analysis
        if self.verbose:
            print("Lexical analysis...")
        
        self.lexer = Lexer(source)
        tokens = self.lexer.tokenize()
        
        if self.verbose:
            print(f"  Generated {len(tokens)} tokens")
        
        # Parsing
        if self.verbose:
            print("Parsing...")
        
        self.parser = Parser(tokens)
        ast = self.parser.parse()
        
        if self.verbose:
            print(f"  Generated {len(ast.declarations)} declarations")
        
        # Semantic Analysis
        if self.verbose:
            print("Semantic analysis...")
        
        self.semantic_analyzer = SemanticAnalyzer()
        self.semantic_analyzer.ctx.current_file = chunk_name
        self.semantic_analyzer.analyze(ast)
        
        if self.verbose:
            diag_count = self.semantic_analyzer.diagnostics.error_count
            print(f"  Semantic analysis complete ({diag_count} errors)")
        
        if self.semantic_analyzer.has_errors:
            raise RuntimeError(
                f"Semantic errors:\n{self.semantic_analyzer.diagnostics.format_all()}"
            )
        
        # Code Generation
        if self.verbose:
            print("Code generation...")
        
        self.code_generator = CodeGenerator()
        chunk = self.code_generator.generate(ast, chunk_name)
        
        if self.verbose:
            print(f"  Generated {len(chunk.code)} instructions")
            print(f"  {len(chunk.constants)} constants")
        
        return chunk
    
    def run_file(self, file_path: str) -> any:
        """
        Compile and run a file.
        
        Args:
            file_path: Path to the source file
            
        Returns:
            Result of execution
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            LexerError: If there's a lexical error
            ParseError: If there's a parse error
            SemanticError: If there's a semantic error
            VMRuntimeError: If there's a runtime error
        """
        chunk = self.compile_file(file_path)
        return self.run_chunk(chunk)
    
    def run_source(self, source: str) -> any:
        """
        Compile and run source code.
        
        Args:
            source: Source code to run
            
        Returns:
            Result of execution
            
        Raises:
            LexerError: If there's a lexical error
            ParseError: If there's a parse error
            SemanticError: If there's a semantic error
            VMRuntimeError: If there's a runtime error
        """
        chunk = self.compile_source(source)
        return self.run_chunk(chunk)
    
    def run_chunk(self, chunk: Chunk) -> any:
        """
        Run a bytecode chunk.
        
        Args:
            chunk: Bytecode chunk to execute
            
        Returns:
            Result of execution
            
        Raises:
            VMRuntimeError: If there's a runtime error
        """
        if self.verbose:
            print("Executing...")
        
        self.vm = VirtualMachine()
        result = self.vm.interpret(chunk)
        
        if self.verbose:
            print("Execution complete")
        
        return result
    
    def disassemble(self, chunk: Chunk) -> str:
        """
        Disassemble a bytecode chunk.
        
        Args:
            chunk: Bytecode chunk to disassemble
            
        Returns:
            Human-readable disassembly
        """
        return chunk.disassemble()


def main():
    """Main entry point for the I compiler."""
    parser = argparse.ArgumentParser(
        description="I Programming Language Compiler",
        epilog="I - The world's first professional programming language designed around Kinyarwanda"
    )
    
    parser.add_argument(
        'file',
        nargs='?',
        help='Source file to compile or run'
    )
    
    parser.add_argument(
        '-r', '--run',
        action='store_true',
        help='Run the compiled code'
    )
    
    parser.add_argument(
        '-d', '--disassemble',
        action='store_true',
        help='Disassemble the bytecode'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Output file for bytecode'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='I Programming Language Compiler v0.1.0'
    )
    
    args = parser.parse_args()
    
    if not args.file:
        parser.print_help()
        sys.exit(1)
    
    compiler = Compiler(verbose=args.verbose)
    
    try:
        # Compile the file
        chunk = compiler.compile_file(args.file)
        
        # Disassemble if requested
        if args.disassemble:
            print(compiler.disassemble(chunk))
        
        # Run if requested
        if args.run:
            result = compiler.run_chunk(chunk)
            if result is not None:
                print(f"Result: {result}")
        
        # Save bytecode if output specified
        if args.output:
            import pickle
            with open(args.output, 'wb') as f:
                pickle.dump(chunk, f)
            if args.verbose:
                print(f"Bytecode saved to {args.output}")
        
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    
    except LexerError as e:
        print(f"Lexical Error: {e}", file=sys.stderr)
        sys.exit(1)
    
    except ParseError as e:
        print(f"Parse Error: {e}", file=sys.stderr)
        sys.exit(1)
    
    except RuntimeError as e:
        if "Semantic errors" in str(e):
            print(str(e), file=sys.stderr)
            sys.exit(1)
        raise
    
    except VMRuntimeError as e:
        print(f"Runtime Error: {e}", file=sys.stderr)
        sys.exit(1)
    
    except Exception as e:
        print(f"Unexpected Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
