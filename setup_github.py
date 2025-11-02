#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GitHub Token设置助手
帮助用户快速设置GitHub Personal Access Token并推送代码
"""

import os
import subprocess
import webbrowser

def setup_github_token():
    """设置GitHub token并推送代码"""
    print("🚀 GitHub Token设置助手")
    print("=" * 50)
    
    # 1. 打开GitHub token生成页面
    print("📖 正在打开GitHub token生成页面...")
    webbrowser.open("https://github.com/settings/tokens")
    
    # 2. 获取用户输入
    print("\n" + "=" * 50)
    print("📋 请按照以下步骤操作:")
    print("1. 在打开的页面中点击 'Generate new token (classic)'")
    print("2. 勾选 'repo' 权限 (完整仓库访问权限)")
    print("3. 点击 'Generate token'")
    print("4. 复制生成的token (注意: token只显示一次)")
    print("=" * 50)
    
    token = input("\n🔑 请输入您的GitHub Personal Access Token: ").strip()
    
    if not token:
        print("❌ Token不能为空")
        return False
    
    if not token.startswith('ghp_'):
        print("⚠️  警告: GitHub token通常以'ghp_'开头")
        confirm = input("是否继续? (y/n): ").strip().lower()
        if confirm != 'y':
            return False
    
    # 3. 设置Git远程URL
    try:
        remote_url = f"https://huojichuanqi:{token}@github.com/huojichuanqi/ds.git"
        print(f"🔧 正在设置Git远程URL...")
        
        result = subprocess.run([
            'git', 'remote', 'set-url', 'origin', remote_url
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ 设置远程URL失败: {result.stderr}")
            return False
        
        print("✅ Git远程URL设置成功")
        
    except Exception as e:
        print(f"❌ 设置远程URL时出错: {e}")
        return False
    
    # 4. 推送代码
    try:
        print("📤 正在推送代码到GitHub...")
        
        result = subprocess.run([
            'git', 'push', 'origin', 'main'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("🎉 代码推送成功!")
            print("📁 您的项目现在可以在GitHub上访问: https://github.com/huojichuanqi/ds")
            return True
        else:
            print(f"❌ 推送失败: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 推送时出错: {e}")
        return False

def manual_instructions():
    """显示手动设置说明"""
    print("\n" + "=" * 60)
    print("📖 手动设置说明")
    print("=" * 60)
    
    print("""
如果您想手动设置，请执行以下命令:

1. 获取GitHub Personal Access Token:
   访问: https://github.com/settings/tokens

2. 设置Git远程URL:
   git remote set-url origin https://huojichuanqi:YOUR_TOKEN@github.com/huojichuanqi/ds.git

3. 推送代码:
   git push origin main

示例:
   git remote set-url origin https://huojichuanqi:ghp_1234567890abcdef@github.com/huojichuanqi/ds.git
   git push origin main
""")

def main():
    """主函数"""
    print("🤖 AI交易机器人 - GitHub推送助手")
    print("=" * 50)
    
    choice = input("选择设置方式:\n1. 自动设置 (推荐)\n2. 手动说明\n请输入选择 (1/2): ").strip()
    
    if choice == '1':
        success = setup_github_token()
        if not success:
            manual_instructions()
    elif choice == '2':
        manual_instructions()
    else:
        print("❌ 无效选择")
        manual_instructions()

if __name__ == "__main__":
    main()
