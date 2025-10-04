#!/usr/bin/env python3
"""
Modern build system for fbundle.github.io
Replaces the Makefile with a Python-based solution
"""
import argparse
import os
import pathlib
import subprocess
import sys
import time
import shutil
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from pathlib import Path
import json

@dataclass
class BuildConfig:
    """Configuration for the build system"""
    tmp_dir: str = "tmp"
    build_dir: str = "build"
    vitae_input_path: Optional[str] = None
    vitae_output_dir: str = "docs/assets/vitae"
    pages_input_dir: str = "src/pages"
    pages_output_dir: str = "docs/pages"
    pages_template_path: str = "src/template.html"
    ts_input_path: str = "src/post-script.ts"
    js_output_dir: str = "docs/js"
    public_doc_input_path: Optional[str] = None
    public_doc_html_dir: str = "/assets/public_doc"
    public_doc_output_dir: str = "docs/assets/public_doc"

class BuildCache:
    """Simple file-based build cache for incremental builds"""
    
    def __init__(self, cache_file: str = ".build_cache.json"):
        self.cache_file = cache_file
        self.cache = self._load_cache()
    
    def _load_cache(self) -> Dict[str, Any]:
        """Load cache from file"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}
    
    def _save_cache(self):
        """Save cache to file"""
        with open(self.cache_file, 'w') as f:
            json.dump(self.cache, f, indent=2)
    
    def get_file_hash(self, file_path: str) -> str:
        """Get a simple hash of file modification time and size"""
        if not os.path.exists(file_path):
            return ""
        stat = os.stat(file_path)
        return f"{stat.st_mtime}_{stat.st_size}"
    
    def is_stale(self, target: str, dependencies: List[str]) -> bool:
        """Check if target is stale compared to dependencies"""
        if target not in self.cache:
            return True
        
        cached_hash = self.cache[target]
        current_hash = self.get_file_hash(target)
        
        # Check if target file changed
        if cached_hash != current_hash:
            return True
        
        # Check if any dependencies changed
        for dep in dependencies:
            dep_hash = self.get_file_hash(dep)
            if dep not in self.cache.get("dependencies", {}) or self.cache["dependencies"][dep] != dep_hash:
                return True
        
        return False
    
    def update_cache(self, target: str, dependencies: List[str]):
        """Update cache after successful build"""
        if "dependencies" not in self.cache:
            self.cache["dependencies"] = {}
        
        self.cache[target] = self.get_file_hash(target)
        for dep in dependencies:
            self.cache["dependencies"][dep] = self.get_file_hash(dep)
        
        self._save_cache()

class Builder:
    """Main build system class"""
    
    def __init__(self, config: BuildConfig):
        self.config = config
        self.cache = BuildCache()
        self.setup_paths()
        self.verbose = False
    
    def setup_paths(self):
        """Auto-detect paths if not specified"""
        if not self.config.vitae_input_path:
            vitae_files = list(Path(".").rglob("**/vitae/main.tex"))
            if vitae_files:
                self.config.vitae_input_path = str(vitae_files[0])
                print(f"🔍 Auto-detected vitae input: {self.config.vitae_input_path}")
        
        if not self.config.public_doc_input_path:
            public_doc_dirs = list(Path(".").rglob("**/public_doc"))
            if public_doc_dirs:
                self.config.public_doc_input_path = str(public_doc_dirs[0])
                print(f"🔍 Auto-detected public doc input: {self.config.public_doc_input_path}")
    
    def log(self, message: str, level: str = "INFO"):
        """Log messages with consistent formatting"""
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
    
    def run_command(self, cmd: List[str], description: str, cwd: Optional[str] = None) -> bool:
        """Run a command with error handling"""
        self.log(f"🔄 {description}...")
        
        if self.verbose:
            self.log(f"Running: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd, 
                check=True, 
                capture_output=not self.verbose, 
                text=True,
                cwd=cwd
            )
            
            if self.verbose and result.stdout:
                print(result.stdout)
            
            self.log(f"✅ {description} completed", "SUCCESS")
            return True
            
        except subprocess.CalledProcessError as e:
            self.log(f"❌ {description} failed: {e}", "ERROR")
            if not self.verbose:
                if e.stdout:
                    print(f"stdout: {e.stdout}")
                if e.stderr:
                    print(f"stderr: {e.stderr}")
            return False
        except FileNotFoundError as e:
            self.log(f"❌ Command not found: {e}", "ERROR")
            return False
    
    def ensure_dir(self, path: str):
        """Ensure directory exists"""
        Path(path).mkdir(parents=True, exist_ok=True)
    
    def build_vitae(self) -> bool:
        """Build vitae from LaTeX"""
        if not self.config.vitae_input_path:
            self.log("⚠️  Skipping vitae build - no input path found", "WARNING")
            return True
        
        if not os.path.exists(self.config.vitae_input_path):
            self.log(f"⚠️  Vitae input file not found: {self.config.vitae_input_path}", "WARNING")
            return True
        
        target = f"{self.config.vitae_output_dir}/main.html"
        dependencies = [self.config.vitae_input_path]
        
        # Check if build is needed
        if not self.cache.is_stale(target, dependencies):
            self.log("📋 Vitae is up to date, skipping build")
            return True
        
        self.ensure_dir(self.config.vitae_output_dir)
        
        cmd = [
            "make4ht",
            "--output-dir", self.config.vitae_output_dir,
            "--build-dir", self.config.tmp_dir,
            self.config.vitae_input_path
        ]
        
        success = self.run_command(cmd, "Building vitae")
        if success:
            self.cache.update_cache(target, dependencies)
        
        return success
    
    def build_pages(self) -> bool:
        """Build HTML pages"""
        target = f"{self.config.pages_output_dir}/.stamp"
        
        # Find all HTML source files
        html_sources = list(Path(self.config.pages_input_dir).rglob("*.html"))
        dependencies = [self.config.pages_template_path] + [str(p) for p in html_sources]
        
        # Check if build is needed
        if not self.cache.is_stale(target, dependencies):
            self.log("📋 Pages are up to date, skipping build")
            return True
        
        self.ensure_dir(self.config.pages_output_dir)
        
        cmd = [
            sys.executable, "bin/generate_pages.py",
            "--input_dir", self.config.pages_input_dir,
            "--output_dir", self.config.pages_output_dir,
            "--template", self.config.pages_template_path
        ]
        
        success = self.run_command(cmd, "Generating pages")
        if success:
            # Create stamp file
            Path(target).touch()
            self.cache.update_cache(target, dependencies)
        
        return success
    
    def copy_public_doc(self) -> bool:
        """Copy public documents"""
        if not self.config.public_doc_input_path:
            self.log("⚠️  Skipping public doc copy - no input path found", "WARNING")
            return True
        
        if not os.path.exists(self.config.public_doc_input_path):
            self.log(f"⚠️  Public doc input not found: {self.config.public_doc_input_path}", "WARNING")
            return True
        
        target = f"{self.config.public_doc_output_dir}/.stamp"
        dependencies = [self.config.public_doc_input_path]
        
        # Check if copy is needed
        if not self.cache.is_stale(target, dependencies):
            self.log("📋 Public docs are up to date, skipping copy")
            return True
        
        self.ensure_dir(self.config.public_doc_output_dir)
        
        cmd = [
            "rsync", "-avh", "--delete", "--progress",
            self.config.public_doc_input_path,
            self.config.public_doc_output_dir
        ]
        
        success = self.run_command(cmd, "Copying public documents")
        if success:
            # Create stamp file
            Path(target).touch()
            self.cache.update_cache(target, dependencies)
        
        return success
    
    def build_text(self) -> bool:
        """Build text index"""
        target = self.config.pages_output_dir + "/posts/text.html"
        dependencies = [
            "bin/generate_text.py",
            "docs/pages/posts/text.template.html"
        ]
        
        # Check if build is needed
        if not self.cache.is_stale(target, dependencies):
            self.log("📋 Text index is up to date, skipping build")
            return True
        
        cmd = [
            sys.executable, "bin/generate_text.py",
            "--html_root_dir", "docs",
            "--doc_htmldir", self.config.public_doc_html_dir,
            "--text_template_path", "docs/pages/posts/text.template.html",
            "--text_output_path", "docs/pages/posts/text.html"
        ]
        
        success = self.run_command(cmd, "Generating text index")
        if success:
            self.cache.update_cache(target, dependencies)
        
        return success
    
    def build_javascript(self) -> bool:
        """Compile TypeScript"""
        target = f"{self.config.js_output_dir}/post-script.js"
        dependencies = [self.config.ts_input_path]
        
        # Check if build is needed
        if not self.cache.is_stale(target, dependencies):
            self.log("📋 JavaScript is up to date, skipping build")
            return True
        
        self.ensure_dir(self.config.js_output_dir)
        
        cmd = [
            "tsc", self.config.ts_input_path,
            "--outDir", self.config.js_output_dir,
            "--target", "ES2020",
            "--module", "ES2020",
            "--strict"
        ]
        
        success = self.run_command(cmd, "Compiling TypeScript")
        if success:
            self.cache.update_cache(target, dependencies)
        
        return success
    
    def build_all(self) -> bool:
        """Build everything"""
        self.log("🚀 Starting build...", "INFO")
        
        steps = [
            (self.build_vitae, "Vitae"),
            (self.build_pages, "Pages"),
            (self.copy_public_doc, "Public docs"),
            (self.build_text, "Text index"),
            (self.build_javascript, "JavaScript")
        ]
        
        success = True
        for step_func, step_name in steps:
            if not step_func():
                self.log(f"💥 Build failed at {step_name}", "ERROR")
                success = False
                break
        
        if success:
            self.log("🎉 Build completed successfully!", "SUCCESS")
        else:
            self.log("💥 Build failed!", "ERROR")
            sys.exit(1)
        
        return success
    
    def watch(self):
        """Watch for changes and rebuild"""
        self.log("👀 Watching for changes... (Ctrl+C to stop)", "INFO")
        
        try:
            while True:
                time.sleep(2)  # Check every 2 seconds
                self.log("🔍 Checking for changes...", "INFO")
                self.build_all()
                
        except KeyboardInterrupt:
            self.log("👋 Stopping watch mode", "INFO")
    
    def clean(self):
        """Clean build artifacts"""
        self.log("🧹 Cleaning build artifacts...", "INFO")
        
        dirs_to_clean = [
            self.config.tmp_dir,
            self.config.build_dir,
            self.config.vitae_output_dir,
            self.config.pages_output_dir,
            self.config.js_output_dir,
            self.config.public_doc_output_dir
        ]
        
        for dir_path in dirs_to_clean:
            if os.path.exists(dir_path):
                shutil.rmtree(dir_path)
                self.log(f"Removed {dir_path}")
        
        # Remove cache and stamp files
        if os.path.exists(".build_cache.json"):
            os.remove(".build_cache.json")
        
        stamp_files = list(Path(".").rglob("*.stamp"))
        for stamp in stamp_files:
            stamp.unlink()
            self.log(f"Removed {stamp}")
        
        self.log("🧹 Clean complete!", "SUCCESS")
    
    def validate(self):
        """Validate configuration and dependencies"""
        self.log("🔍 Validating configuration...", "INFO")
        
        errors = []
        warnings = []
        
        # Check required tools
        required_tools = {
            "make4ht": "LaTeX to HTML conversion",
            "tsc": "TypeScript compiler",
            "rsync": "File synchronization",
            "python": "Python interpreter"
        }
        
        for tool, description in required_tools.items():
            if tool == "python":
                tool_path = sys.executable
            else:
                tool_path = shutil.which(tool)
            
            if tool_path:
                self.log(f"✅ {tool} found: {tool_path}")
            else:
                errors.append(f"❌ {tool} not found (needed for {description})")
        
        # Check input files
        if self.config.vitae_input_path and not os.path.exists(self.config.vitae_input_path):
            warnings.append(f"⚠️  Vitae input not found: {self.config.vitae_input_path}")
        
        if self.config.public_doc_input_path and not os.path.exists(self.config.public_doc_input_path):
            warnings.append(f"⚠️  Public doc input not found: {self.config.public_doc_input_path}")
        
        # Check Python scripts
        python_scripts = ["bin/generate_pages.py", "bin/generate_text.py"]
        for script in python_scripts:
            if os.path.exists(script):
                self.log(f"✅ {script} found")
            else:
                errors.append(f"❌ {script} not found")
        
        # Report results
        if warnings:
            self.log("Warnings:", "WARNING")
            for warning in warnings:
                self.log(f"  {warning}", "WARNING")
        
        if errors:
            self.log("Errors:", "ERROR")
            for error in errors:
                self.log(f"  {error}", "ERROR")
            self.log("❌ Validation failed!", "ERROR")
            return False
        else:
            self.log("✅ Configuration validated!", "SUCCESS")
            return True
    
    def status(self):
        """Show build status"""
        self.log("📊 Build status:", "INFO")
        
        targets = [
            ("Vitae", f"{self.config.vitae_output_dir}/main.html"),
            ("Pages", f"{self.config.pages_output_dir}/.stamp"),
            ("Public docs", f"{self.config.public_doc_output_dir}/.stamp"),
            ("Text index", f"{self.config.pages_output_dir}/posts/text.html"),
            ("JavaScript", f"{self.config.js_output_dir}/post-script.js")
        ]
        
        for name, target in targets:
            if os.path.exists(target):
                mtime = time.ctime(os.path.getmtime(target))
                self.log(f"  {name}: ✅ {target} (modified: {mtime})")
            else:
                self.log(f"  {name}: ❌ {target} (not built)")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Modern build system for fbundle.github.io",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python build.py                    # Build everything
  python build.py --watch           # Watch for changes
  python build.py --clean           # Clean build artifacts
  python build.py --validate        # Validate configuration
  python build.py --status          # Show build status
  python build.py --verbose         # Verbose output
        """
    )
    
    parser.add_argument("--watch", action="store_true", help="Watch for changes and rebuild")
    parser.add_argument("--clean", action="store_true", help="Clean build artifacts")
    parser.add_argument("--validate", action="store_true", help="Validate configuration")
    parser.add_argument("--status", action="store_true", help="Show build status")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # Initialize configuration
    config = BuildConfig()
    builder = Builder(config)
    builder.verbose = args.verbose
    
    # Show help if no arguments
    if len(sys.argv) == 1:
        parser.print_help()
        return
    
    # Execute requested action
    if args.clean:
        builder.clean()
    elif args.validate:
        builder.validate()
    elif args.status:
        builder.status()
    elif args.watch:
        builder.watch()
    else:
        # Default: build everything
        if builder.validate():
            builder.build_all()
        else:
            sys.exit(1)

if __name__ == "__main__":
    main()
