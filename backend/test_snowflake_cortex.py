#!/usr/bin/env python3
"""
Snowflake Cortex Search 测试脚本
用于单独测试 Snowflake Cortex Search 的搜索功能和结果

使用方法:
    python test_snowflake_cortex.py "你的搜索查询"
    或
    python test_snowflake_cortex.py  # 交互式模式
"""

import sys
import json
import os
import asyncio
import logging
from pathlib import Path

# 尝试加载 .env 文件（在导入其他模块之前）
try:
    from dotenv import load_dotenv
    project_root = Path(__file__).parent.parent
    env_file = project_root / ".env"
    if env_file.exists():
        load_dotenv(env_file)
        print(f"✅ 已加载环境变量文件: {env_file}")
    else:
        print(f"⚠️  未找到 .env 文件: {env_file}")
except ImportError:
    print("⚠️  python-dotenv 未安装，将使用系统环境变量")
except Exception as e:
    print(f"⚠️  加载 .env 文件时出错: {e}")

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
log = logging.getLogger(__name__)

# 添加项目路径以便导入模块
sys.path.insert(0, str(Path(__file__).parent))

from open_webui.utils.snowflake_cortex import (
    SnowflakeCortexSearch,
    get_snowflake_client,
    search_snowflake_cortex,
    SNOWFLAKE_AVAILABLE
)

# 必需的环境变量列表
REQUIRED_ENV_VARS = [
    "SNOWFLAKE_ACCOUNT",
    "SNOWFLAKE_USER",
    "SNOWFLAKE_ROLE",
    "SNOWFLAKE_WAREHOUSE",
    "SNOWFLAKE_DATABASE",
    "SNOWFLAKE_SCHEMA",
    "SNOWFLAKE_CORTEX_SERVICE",
]

# 可选的环境变量（至少需要其中一个）
OPTIONAL_AUTH_VARS = [
    "SNOWFLAKE_PASSWORD",
    "SNOWFLAKE_PRIVATE_KEY_PEM",
]


def check_environment_variables():
    """检查环境变量是否设置"""
    missing_vars = []
    missing_auth = True
    
    # 检查必需变量
    for var in REQUIRED_ENV_VARS:
        value = os.getenv(var, "")
        if not value:
            missing_vars.append(var)
    
    # 检查认证变量（至少需要一个）
    for var in OPTIONAL_AUTH_VARS:
        if os.getenv(var, ""):
            missing_auth = False
            break
    
    return missing_vars, missing_auth


def print_environment_check():
    """打印环境变量检查结果"""
    print("🔍 检查环境变量配置...")
    print_separator()
    
    missing_vars, missing_auth = check_environment_variables()
    
    if missing_vars:
        print("❌ 缺少以下必需的环境变量:")
        for var in missing_vars:
            print(f"   - {var}")
        print()
    
    if missing_auth:
        print("❌ 缺少认证信息，需要设置以下环境变量之一:")
        for var in OPTIONAL_AUTH_VARS:
            print(f"   - {var}")
        print()
    
    if missing_vars or missing_auth:
        print("💡 配置方法:")
        print("   1. 在项目根目录创建 .env 文件")
        print("   2. 或在系统环境变量中设置")
        print()
        print("📝 .env 文件示例:")
        print("   SNOWFLAKE_ACCOUNT=your_account")
        print("   SNOWFLAKE_USER=your_user")
        print("   SNOWFLAKE_PASSWORD=your_password")
        print("   SNOWFLAKE_ROLE=your_role")
        print("   SNOWFLAKE_WAREHOUSE=your_warehouse")
        print("   SNOWFLAKE_DATABASE=your_database")
        print("   SNOWFLAKE_SCHEMA=your_schema")
        print("   SNOWFLAKE_CORTEX_SERVICE=your_service_name")
        print()
        
        # 检查 .env 文件是否存在
        env_file = Path(__file__).parent.parent / ".env"
        if not env_file.exists():
            print(f"⚠️  未找到 .env 文件: {env_file}")
            print("   请创建该文件并添加配置")
        else:
            print(f"✅ 找到 .env 文件: {env_file}")
            print("   请检查文件内容是否正确")
        
        print_separator()
        return False
    
    print("✅ 所有必需的环境变量都已设置")
    print_separator()
    
    # 显示已设置的变量（隐藏敏感信息）
    print("📋 环境变量状态:")
    for var in REQUIRED_ENV_VARS:
        value = os.getenv(var, "")
        display_value = value[:20] + "..." if len(value) > 20 else value
        print(f"   ✅ {var}: {display_value}")
    
    for var in OPTIONAL_AUTH_VARS:
        value = os.getenv(var, "")
        if value:
            display_value = "***已设置***" if var == "SNOWFLAKE_PASSWORD" else "***已设置***"
            print(f"   ✅ {var}: {display_value}")
        else:
            print(f"   ⚪ {var}: 未设置")
    
    print_separator()
    return True


def print_separator():
    """打印分隔线"""
    print("\n" + "=" * 80 + "\n")


def print_config_info(client: SnowflakeCortexSearch):
    """打印配置信息（隐藏敏感信息）"""
    print("📋 Snowflake 配置信息:")
    print(f"  Account: {client.account}")
    print(f"  User: {client.user}")
    print(f"  Role: {client.role}")
    print(f"  Warehouse: {client.warehouse}")
    print(f"  Database: {client.database}")
    print(f"  Schema: {client.schema}")
    print(f"  Cortex Service: {client.cortex_service}")
    print(f"  Authentication: {'Private Key' if client.private_key_pem else 'Password'}")
    print_separator()


def print_raw_results(results: dict):
    """打印原始搜索结果（JSON格式）"""
    print("📦 原始搜索结果 (JSON):")
    print(json.dumps(results, indent=2, ensure_ascii=False))
    print_separator()


def print_formatted_results(formatted: str):
    """打印格式化后的搜索结果"""
    print("📄 格式化后的搜索结果:")
    print(formatted)
    print_separator()


def print_summary(results: dict):
    """打印结果摘要"""
    if not results or "results" not in results:
        print("❌ 没有找到搜索结果")
        return
    
    result_list = results.get("results", [])
    print(f"✅ 找到 {len(result_list)} 条搜索结果")
    
    for idx, result in enumerate(result_list, 1):
        file_name = result.get("FILE_NAME", "Unknown")
        file_source = result.get("FILE_SOURCE", "Unknown")
        content_preview = result.get("CONTENT", "")[:100] + "..." if len(result.get("CONTENT", "")) > 100 else result.get("CONTENT", "")
        
        print(f"\n  结果 {idx}:")
        print(f"    📁 文件: {file_source} / {file_name}")
        print(f"    📝 内容预览: {content_preview}")
    print_separator()


def test_search_sync(query: str, limit: int = 5):
    """同步方式测试搜索"""
    print(f"🔍 执行搜索查询: '{query}'")
    print(f"📊 结果限制: {limit}")
    print_separator()
    
    # 先检查环境变量
    if not print_environment_check():
        print("❌ 环境变量配置不完整，无法继续测试")
        return False
    
    try:
        # 创建客户端
        print("🔧 初始化 Snowflake Cortex Search 客户端...")
        client = SnowflakeCortexSearch()
        print_config_info(client)
        
        # 执行搜索
        print(f"🚀 开始搜索...")
        results = client.search(query=query, limit=limit)
        
        if results:
            print_summary(results)
            print_raw_results(results)
            
            # 格式化结果
            formatted = client.format_search_results(results)
            if formatted:
                print_formatted_results(formatted)
            
            # 关闭连接
            client.close()
            print("✅ 测试完成！")
            return True
        else:
            print("❌ 搜索返回空结果")
            client.close()
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_search_async(query: str, limit: int = 5):
    """异步方式测试搜索（使用高级API）"""
    print(f"🔍 执行搜索查询 (异步): '{query}'")
    print(f"📊 结果限制: {limit}")
    print_separator()
    
    try:
        print("🚀 开始搜索...")
        formatted_results = await search_snowflake_cortex(query=query, limit=limit)
        
        if formatted_results:
            print_formatted_results(formatted_results)
            print("✅ 测试完成！")
            return True
        else:
            print("❌ 搜索返回空结果")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def interactive_mode():
    """交互式测试模式"""
    print("=" * 80)
    print("🎯 Snowflake Cortex Search 交互式测试")
    print("=" * 80)
    print()
    
    if not SNOWFLAKE_AVAILABLE:
        print("❌ Snowflake 库未安装，请先运行: pip install snowflake snowflake-snowpark-python")
        return
    
    # 先检查环境变量
    if not print_environment_check():
        print("❌ 环境变量配置不完整，无法继续测试")
        return
    
    try:
        # 测试连接
        print("🔧 测试连接...")
        client = SnowflakeCortexSearch()
        print("✅ 连接成功！")
        print_config_info(client)
        client.close()
        
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        print("\n💡 请检查:")
        print("   1. 环境变量是否正确设置")
        print("   2. Snowflake 账户权限是否足够")
        print("   3. 网络连接是否正常")
        import traceback
        traceback.print_exc()
        return
    
    print("\n" + "=" * 80)
    print("开始交互式测试...")
    print("输入 'quit' 或 'exit' 退出")
    print("=" * 80 + "\n")
    
    while True:
        try:
            query = input("请输入搜索查询 (或 'quit' 退出): ").strip()
            
            if not query or query.lower() in ['quit', 'exit', 'q']:
                print("👋 再见！")
                break
            
            if query.lower() == 'help':
                print("\n可用命令:")
                print("  help - 显示帮助")
                print("  quit/exit/q - 退出")
                print("  其他任何文本 - 作为搜索查询")
                print()
                continue
            
            # 询问结果数量
            limit_input = input("结果数量限制 (默认5，直接回车使用默认值): ").strip()
            limit = int(limit_input) if limit_input.isdigit() else 5
            
            print_separator()
            success = test_search_sync(query, limit)
            
            if success:
                print("✅ 搜索成功完成")
            else:
                print("❌ 搜索失败")
            
            print_separator()
            
        except KeyboardInterrupt:
            print("\n\n👋 再见！")
            break
        except Exception as e:
            print(f"\n❌ 发生错误: {e}")
            import traceback
            traceback.print_exc()


def main():
    """主函数"""
    if not SNOWFLAKE_AVAILABLE:
        print("❌ Snowflake 库未安装")
        print("💡 请运行: pip install snowflake snowflake-snowpark-python")
        sys.exit(1)
    
    # 检查命令行参数
    if len(sys.argv) > 1:
        # 如果只是检查环境变量
        if sys.argv[1] in ["--check-env", "-c", "check"]:
            print_environment_check()
            sys.exit(0)
        query = " ".join(sys.argv[1:])
        limit = 5
        
        # 检查是否有 --limit 参数
        if "--limit" in sys.argv:
            limit_idx = sys.argv.index("--limit")
            if limit_idx + 1 < len(sys.argv):
                try:
                    limit = int(sys.argv[limit_idx + 1])
                except ValueError:
                    print("❌ --limit 参数必须是数字")
                    sys.exit(1)
        
        # 执行同步测试
        success = test_search_sync(query, limit)
        sys.exit(0 if success else 1)
    else:
        # 交互式模式
        interactive_mode()


if __name__ == "__main__":
    main()
