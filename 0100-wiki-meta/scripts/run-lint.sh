#!/bin/bash
# 知识库健康检查总入口
# 整合 10 项 lint 检查，详见 CLAUDE.md § Lint

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WIKI_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

cd "$WIKI_ROOT"

echo "=== Mnemosyne Lint 健康检查 ==="
echo ""

# 计数器
total_checks=0
passed_checks=0
failed_checks=0
skipped_checks=0

# 辅助函数
run_check() {
    local name="$1"
    local script="$2"
    local severity="${3:-WARNING}"

    total_checks=$((total_checks + 1))
    echo "[$total_checks] $name"

    if [[ ! -f "$script" ]]; then
        echo "  [SKIP] 脚本不存在: $script"
        skipped_checks=$((skipped_checks + 1))
        echo ""
        return
    fi

    if python "$script" > /tmp/lint_$total_checks.log 2>&1; then
        echo "  [PASS]"
        passed_checks=$((passed_checks + 1))
    else
        exit_code=$?

        if [[ "$exit_code" -eq 1 && "$severity" == "WARNING" ]]; then
            echo "  [WARN] 发现警告"
            passed_checks=$((passed_checks + 1))
        else
            echo "  [FAIL] 退出码: $exit_code"
            cat /tmp/lint_$total_checks.log | head -20
            failed_checks=$((failed_checks + 1))

            if [[ "$severity" == "CRITICAL" ]]; then
                echo ""
                echo "!!! CRITICAL 检查失败，中止 lint 流程 !!!"
                exit 1
            fi
        fi
    fi
    echo ""
}

# === 核心检查（已实现） ===

# 1. DB 驱动的聚合检查
run_check "DB 健康检查" "0100-wiki-meta/scripts/check-db-health.py" "WARNING"

# 2. 配置同步检查
run_check "配置同步检查" "0100-wiki-meta/scripts/check-config-sync.py" "CRITICAL"

# 3. Frontmatter 校验
run_check "Frontmatter 校验" "0100-wiki-meta/scripts/validate-frontmatter.py" "WARNING"

# === 待实现检查（占位） ===

# 4. L2 结构完整性（核心提炼区 + 原文笔记区）
echo "[4] L2 结构完整性"
echo "  [SKIP] 待实现"
skipped_checks=$((skipped_checks + 1))
echo ""

# 5. 文件名格式（命名规则：kebab-case, 特殊字符转换）
echo "[5] 文件名格式"
echo "  [SKIP] 待实现"
skipped_checks=$((skipped_checks + 1))
echo ""

# 6. resource_refs 一致性（resource_refs 字段与实际图片路径匹配）
echo "[6] resource_refs 一致性"
echo "  [SKIP] 待实现"
skipped_checks=$((skipped_checks + 1))
echo ""

# 7. 远程图片残留（正文中不应有 http/https 图片链接）
echo "[7] 远程图片残留"
echo "  [SKIP] 待实现"
skipped_checks=$((skipped_checks + 1))
echo ""

# 8. Tags 格式（5-10 个，无空格，连字符连接）
echo "[8] Tags 格式"
echo "  [SKIP] 待实现"
skipped_checks=$((skipped_checks + 1))
echo ""

# 9. Summary 范围（≥200 字）
echo "[9] Summary 范围"
echo "  [SKIP] 待实现"
skipped_checks=$((skipped_checks + 1))
echo ""

# 10. Topic 注册（L2 topic 必须在 topics.yaml active 列表中）
echo "[10] Topic 注册"
echo "  [SKIP] 待实现（部分由 check-config-sync.py 覆盖）"
skipped_checks=$((skipped_checks + 1))
echo ""

# === 汇总报告 ===
echo "=== Lint 汇总 ==="
echo "  总检查项: $total_checks"
echo "  通过: $passed_checks"
echo "  失败: $failed_checks"
echo "  跳过: $skipped_checks"
echo ""

if [[ $failed_checks -gt 0 ]]; then
    echo "!!! 存在 $failed_checks 项失败检查，请查看上述输出 !!!"
    exit 1
else
    echo "[OK] 所有已实现检查通过"
    exit 0
fi
