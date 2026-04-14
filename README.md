# guguzhen-slack

咕咕镇摆烂小工具的简化实现，保留多账号、续密钥、商店、许愿、战斗、翻牌和工坊功能。  
当前版本改为单次顺序执行，不再内置定时调度、日志文件和数据库导出。运行信息直接打印到 stdout。  

## 当前实现

- 配置来源是 `config` 目录下的多个 `.yaml` 文件
- 默认会优先读取项目根目录下的 `config`，也可用 `GUGUZHEN_CONFIG_DIR` 指定其他配置目录
- 每次执行都会先尝试续密钥，随后继续执行其余已开启功能
- 如果站点返回了新的 cookie，会自动回写到对应账号的 yaml 配置
- HTTP 客户端使用 `httpx`，HTML 文本提取使用 `beautifulsoup4`

## 使用说明

1. 安装 Python 3.9 或更高版本。
2. 安装依赖。

```bash
pip install -r requirements.txt
```

1. 在项目根目录创建 `config` 文件夹。
2. 把 [template.yaml](template.yaml) 复制为 `config/账号名.yaml`，每个账号一个文件。
3. 把抓到的 cookie 粘贴到对应 yaml 的 `cookie` 字段。
4. 运行脚本。

```bash
python slack.py
```

如果脚本不是从项目根目录启动，例如容器里直接执行绝对路径脚本，可以显式指定配置目录：

```bash
GUGUZHEN_CONFIG_DIR=/guguzhen/config python /guguzhen/slack.py
```

## 配置说明

- `cookie`: 登录态 cookie，首次需要手动抓取
- `shop.*`: 商店兑换和买药水开关
- `beach.clear_equipment`: 是否清理沙滩装备并回收为锻造石
- `wish`: 是否执行固定 300w 贝壳许愿 11 次
- `fight.*`: 战斗模式、翻牌策略、药水使用次数
- `factory`: 单次运行时执行一次工坊检查，填 `0` 跳过
- `renew_key`: 是否在本次运行开头先执行续密钥，默认开启

## 如何抓 cookie

打开 F12 控制台，切换到网络（Network）选项卡。  
访问 [咕咕镇首页](https://www.momozhen.com/fyg_index.php#)。  
控制台下方左侧会有一排请求，点击第一个，在右侧下拉找到 `Cookie: xxxxx`，把 `xxxxx` 粘到 yaml 配置文件里。  
![示例](https://github.com/user-attachments/assets/d4b57462-3261-49b5-833c-920e0ab8ad70)

## 不再提供的功能

- 不再实现 `scheduler` 定时配置
- 不再写入 `slack.db`
- 不再提供战斗记录导出工具
- 不再生成日志文件

## 说明

项目仍然依赖页面返回结构。游戏页面更新后，如果接口或 HTML 结构变化，部分功能可能需要重新适配。
