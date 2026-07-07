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

# === P0 Lint 补全检查 ===

# 4. L2 结构完整性（核心提炼区 + 原文笔记区）
run_check "L2 结构完整性" "0100-wiki-meta/scripts/check-l2-structure.py" "WARNING"

# 5. 文件名格式（命名规则：kebab-case, 特殊字符转换）
run_check "文件名格式" "0100-wiki-meta/scripts/check-filename-format.py" "WARNING"

# 6. resource_refs 一致性（resource_refs 字段与实际图片路径匹配）
run_check "resource_refs 一致性" "0100-wiki-meta/scripts/check-resource-refs.py" "WARNING"

# 7. 远程图片残留（正文中不应有 http/https 图片链接）
run_check "远程图片残留" "0100-wiki-meta/scripts/check-remote-images.py" "WARNING"

# 8. Tags 格式（5-10 个，无空格，连字符连接）
run_check "Tags 格式" "0100-wiki-meta/scripts/check-tags-format.py" "WARNING"

# 9. Summary 范围（≥200 字）
run_check "Summary 范围" "0100-wiki-meta/scripts/check-summary-length.py" "WARNING"

# 10. Topic 注册（L2 topic 必须在 topics.yaml active 列表中）
run_check "Topic 注册" "0100-wiki-meta/scripts/check-topic-registration.py" "WARNING"

# === E4 置信度系统检查 ===

# 11. 置信度和来源标注完整性
run_check "置信度和来源标注" "0100-wiki-meta/scripts/check-provenance.py" "WARNING"

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
