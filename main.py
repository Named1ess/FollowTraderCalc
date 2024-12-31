import re

# α, β, γ 的值
alpha = 0.35
beta = 0.35
gamma = 0.3


def calculate_composite_profitability(sharpe_ratio, win_rate, max_drawdown, return_rate):
    """
    计算综合盈利系数
    :param sharpe_ratio: 夏普比率
    :param win_rate: 胜率
    :param max_drawdown: 最大回撤
    :param return_rate: 收益率
    :return: 综合盈利系数
    """
    return (alpha * (sharpe_ratio * win_rate)) + (beta * (1 - max_drawdown / 100)) + (gamma * return_rate)


def parse_trader_data(file_path):
    """
    解析文件中的交易员数据
    :param file_path: 文件路径
    :return: 交易员数据字典
    """
    traders = {}

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 匹配每个交易员的数据
    trader_blocks = re.findall(
        r'([^\n]+)\n收益率\n盈亏\n([^\n]+)\n([^\n]+)\n夏普比率\n([^\n]+)\n最大回撤\n([^\n]+)\n胜率\n([^\n]+)', content)

    for block in trader_blocks:
        trader_name = block[0].strip()

        # 处理收益率：移除逗号和百分号，再转换为小数
        return_rate_str = block[1].strip().replace(',', '')  # 去掉逗号
        return_rate = float(return_rate_str.replace('%', '')) / 100  # 去掉百分号并转为小数

        # 处理盈亏：移除逗号
        profit_loss = float(block[2].strip().replace(',', ''))  # 盈亏（去掉逗号并转为浮动值）

        # 其他数据直接转换
        sharpe_ratio = float(block[3].strip())
        max_drawdown = float(block[4].strip().replace('%', ''))  # 转为百分比
        win_rate = float(block[5].strip().replace('%', '')) / 100  # 转为小数

        # 计算综合盈利系数
        composite_profitability = calculate_composite_profitability(sharpe_ratio, win_rate, max_drawdown, return_rate)

        traders[trader_name] = {
            'return_rate': return_rate,
            'profit_loss': profit_loss,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'win_rate': win_rate,
            'composite_profitability': composite_profitability
        }

    return traders


def print_trader_composite_profitability(traders_30, traders_90):
    """
    打印每个交易员的30天、90天和加权后的综合盈利系数，并修改最大最小加权系数
    :param traders_30: 30天周期的交易员数据字典
    :param traders_90: 90天周期的交易员数据字典
    """
    print("交易员的综合盈利系数：")
    print("=" * 40)  # 分隔线

    # 获取所有交易员的名字（假设两个文件中的交易员名字一致）
    trader_names = set(traders_30.keys()).union(set(traders_90.keys()))

    # 保存每个交易员的加权综合盈利系数及其名字
    weighted_data = []

    for trader_name in trader_names:
        # 获取30天和90天的数据
        trader_data_30 = traders_30.get(trader_name)
        trader_data_90 = traders_90.get(trader_name)

        # 如果交易员在两个周期数据中都有
        if trader_data_30 and trader_data_90:
            # 输出30天的综合盈利系数
            weighted_composite = calculate_weighted_composite_profitability(trader_data_30, trader_data_90)
            weighted_data.append((trader_name, weighted_composite))

    # 排序加权综合盈利系数：从大到小
    weighted_data.sort(key=lambda x: x[1], reverse=True)

    # 找出最大和最小的交易员
    max_trader = weighted_data[0]  # 最大
    min_trader = weighted_data[-1]  # 最小

    # 获取第二大和倒数第二大的数据
    second_max_trader = weighted_data[1] if len(weighted_data) > 1 else max_trader
    second_min_trader = weighted_data[-2] if len(weighted_data) > 1 else min_trader

    print("加权后的综合盈利系数：")
    print("=" * 40)

    # 输出每个交易员的加权后的综合盈利系数，并修改最大最小的值
    for trader_name, weighted_composite in weighted_data:
        # 输出修改前的加权系数
        if trader_name == max_trader[0]:
            print(f"交易员: {trader_name}  原加权后的综合盈利系数: {weighted_composite:.4f} (修改后: {second_max_trader[1]:.4f})")
        elif trader_name == min_trader[0]:
            print(f"交易员: {trader_name}  原加权后的综合盈利系数: {weighted_composite:.4f} (修改后: {second_min_trader[1]:.4f})")
        else:
            print(f"交易员: {trader_name}  加权后的综合盈利系数: {weighted_composite:.4f}")

    # 修改最大和最小交易员的加权系数
    traders_30[max_trader[0]]['composite_profitability'] = second_max_trader[1]
    traders_90[max_trader[0]]['composite_profitability'] = second_max_trader[1]
    traders_30[min_trader[0]]['composite_profitability'] = second_min_trader[1]
    traders_90[min_trader[0]]['composite_profitability'] = second_min_trader[1]

    # 计算并输出资金分配百分比
    total_funds = 100000  # 总资金金额，例如100000元
    fund_distribution = calculate_fund_distribution(traders_30, traders_90, total_funds)

    print("\n每个交易员的资金分配百分比：")
    for trader_name, fund_percentage in fund_distribution.items():
        print(f"交易员: {trader_name}  分配百分比: {fund_percentage * 100:.2f}%")


def calculate_weighted_composite_profitability(trader_data_30, trader_data_90):
    """
    计算加权后的综合盈利系数
    :param trader_data_30: 30天周期的交易员数据
    :param trader_data_90: 90天周期的交易员数据
    :return: 加权后的综合盈利系数
    """
    weighted_composite = (trader_data_30['composite_profitability'] * 0.5) + (trader_data_90['composite_profitability'] * 0.5)
    return weighted_composite

def calculate_fund_distribution(traders_30, traders_90, total_funds):
    """
    根据修改后的加权综合盈利系数分配资金
    :param traders_30: 30天周期的交易员数据字典
    :param traders_90: 90天周期的交易员数据字典
    :param total_funds: 总资金
    :return: 每个交易员的资金分配百分比
    """
    # 获取加权后的综合盈利系数
    weighted_data = []

    for trader_name in traders_30.keys():
        trader_data_30 = traders_30[trader_name]
        trader_data_90 = traders_90.get(trader_name)

        if trader_data_90:
            weighted_composite = calculate_weighted_composite_profitability(trader_data_30, trader_data_90)
            weighted_data.append((trader_name, weighted_composite))

    # 排序加权综合盈利系数：从大到小
    weighted_data.sort(key=lambda x: x[1], reverse=True)

    # 找出最大和最小的交易员
    max_trader = weighted_data[0]  # 最大
    min_trader = weighted_data[-1]  # 最小

    # 获取第二大和倒数第二大的数据
    second_max_trader = weighted_data[1] if len(weighted_data) > 1 else max_trader
    second_min_trader = weighted_data[-2] if len(weighted_data) > 1 else min_trader

    # 修改最大和最小交易员的加权系数
    for i in range(len(weighted_data)):
        trader_name, weighted_composite = weighted_data[i]
        if trader_name == max_trader[0]:
            weighted_data[i] = (trader_name, second_max_trader[1])
        elif trader_name == min_trader[0]:
            weighted_data[i] = (trader_name, second_min_trader[1])

    # 计算加权系数的总和
    total_weight = sum(weighted_composite for _, weighted_composite in weighted_data)

    # 为每个交易员分配资金
    fund_distribution = {}
    for trader_name, weighted_composite in weighted_data:
        fund_percentage = weighted_composite / total_weight  # 该交易员的权重占比
        fund_distribution[trader_name] = fund_percentage  # 资金分配百分比

    return fund_distribution

def main():
    # 读取并解析30天周期文件
    traders_30 = parse_trader_data('Trader30.txt')
    # 读取并解析90天周期文件
    traders_90 = parse_trader_data('Trader90.txt')

    # 输出交易员的综合盈利系数及加权后的结果
    print_trader_composite_profitability(traders_30, traders_90)



if __name__ == "__main__":
    main()
