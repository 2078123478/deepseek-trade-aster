#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
创建个人GitHub仓库助手
帮助用户创建自己的GitHub仓库并推送代码
"""

import os
import subprocess
import webbrowser
import getpass

def create_github_repo():
    """创建个人GitHub仓库"""
    print("🚀 创建个人GitHub仓库助手")
    print("=" * 50)
    
    # 1. 获取用户信息
    username = input("👤 请输入您的GitHub用户名: ").strip()
    if not username:
        print("❌ 用户名不能为空")
        return False
    
    repo_name = input("📁 请输入仓库名称 (默认: ai-trading-bot): ").strip()
    if not repo_name:
        repo_name = "ai-trading-bot"
    
    # 2. 设置Git用户信息
    try:
        print("🔧 正在设置Git用户信息...")
        
        email = input("📧 请输入您的GitHub邮箱: ").strip()
        if email:
            subprocess.run(['git', 'config', 'user.name', username], check=True)
            subprocess.run(['git', 'config', 'user.email', email], check=True)
            print("✅ Git用户信息设置成功")
        
    except Exception as e:
        print(f"❌ 设置Git用户信息失败: {e}")
    
    # 3. 打开GitHub创建页面
    create_url = f"https://github.com/new"
    print(f"📖 正在打开GitHub仓库创建页面...")
    webbrowser.open(create_url)
    
    print("\n" + "=" * 50)
    print("📋 请按照以下步骤操作:")
    print(f"1. 仓库名称填写: {repo_name}")
    print("2. 选择 'Public' 或 'Private'")
    print("3. 勾选 'Add a README file' (可选)")
    print("4. 点击 'Create repository'")
    print("=" * 50)
    
    input("\n按Enter键继续，完成仓库创建后...")
    
    # 4. 设置新的远程仓库
    try:
        # 5. 获取GitHub token
        print("\n🔑 请获取GitHub Personal Access Token:")
        webbrowser.open("https://github.com/settings/tokens")
        
        print("\n📋 Token设置步骤:")
        print("1. 点击 'Generate new token (classic)'")
        print("2. 勾选 'repo' 权限")
        print("3. 点击 'Generate token'")
        print("4. 复制生成的token")
        
        token = input("\n🔑 请输入您的GitHub Personal Access Token: ").strip()
        
        if not token:
            print("❌ Token不能为空")
            return False
        
        # 6. 设置远程仓库
        remote_url = f"https://{username}:{token}@github.com/{username}/{repo_name}.git"
        print(f"🔧 正在设置Git远程URL...")
        
        # 先删除旧的远程仓库
        subprocess.run(['git', 'remote', 'remove', 'origin'], capture_output=True)
        
        # 添加新的远程仓库
        result = subprocess.run([
            'git', 'remote', 'add', 'origin', remote_url
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ 设置远程URL失败: {result.stderr}")
            return False
        
        print("✅ Git远程URL设置成功")
        
        # 7. 推送代码
        print("📤 正在推送代码到GitHub...")
        
        result = subprocess.run([
            'git', 'push', '-u', 'origin', 'main'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("🎉 代码推送成功!")
            print(f"📁 您的项目现在可以在GitHub上访问: https://github.com/{username}/{repo_name}")
            print(f"📋 仓库地址: https://github.com/{username}/{repo_name}")
            print(f"🔗 克隆地址: git clone https://github.com/{username}/{repo_name}.git")
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
    
    username = input("👤 请输入您的GitHub用户名: ").strip()
    repo_name = input("📁 请输入仓库名称 (默认: ai-trading-bot): ").strip()
    
    if not repo_name:
        repo_name = "ai-trading-bot"
    
    print(f"""
手动设置步骤:

1. 创建GitHub仓库:
   - 访问: https://github.com/new
   - 仓库名: {repo_name}
   - 选择Public或Private
   - 点击"Create repository"

2. 获取Personal Access Token:
   - 访问: https://github.com/settings/tokens
   - 点击"Generate new token (classic)"
   - 勾选"repo"权限
   - 复制生成的token

3. 设置Git远程仓库:
   git remote remove origin
   git remote add origin https://{username}:YOUR_TOKEN@github.com/{username}/{repo_name}.git

4. 推送代码:
   git push -u origin main

完成后访问: https://github.com/{username}/{repo_name}
""")

def main():
    """主函数"""
    print("🤖 AI交易机器人 - 创建个人GitHub仓库")
    print("=" * 50)
    
    choice = input("选择设置方式:\n1. 自动创建 (推荐)\n2. 手动说明\n请输入选择 (1/2): ").strip()
    
    if choice == '1':
        success = create_github_repo()
        if not success:
            manual_instructions()
    elif choice == '2':
        manual_instructions()
    else:
        print("❌ 无效选择")
        manual_instructions()

if __name__ == "__main__":
    main()
