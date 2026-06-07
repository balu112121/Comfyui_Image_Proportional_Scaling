// 图像等比倍数缩放节点前端增强脚本

import { app } from "../../../scripts/app.js";

// 注册插件扩展
app.registerExtension({
    name: "Comfyui.ImageProportionalScaling",
    
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        // 只为特定节点添加功能
        if (nodeData.name === "Comfyui_Image_Proportional_Scaling") {
            
            // 在节点创建时添加额外控件
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function() {
                const result = onNodeCreated ? onNodeCreated.apply(this, arguments) : undefined;
                
                // 添加使用提示
                this.addWidget("text", "使用提示", "等比缩放 | 独立开关控制", () => {});
                
                // 添加美化样式
                if (this.widgets) {
                    const scaleWidget = this.widgets.find(w => w.name === "缩放倍数");
                    if (scaleWidget) {
                        scaleWidget.configStep = 0.01;
                    }
                }
                
                return result;
            };
            
            // 添加节点执行后的回调
            const onExecuted = nodeType.prototype.onExecuted;
            nodeType.prototype.onExecuted = function(message) {
                if (onExecuted) {
                    onExecuted.apply(this, arguments);
                }
                
                // 可以在执行后显示尺寸信息
                if (message && message.output && message.output.width && message.output.height) {
                    this.hint = `输出尺寸: ${message.output.width} x ${message.output.height}`;
                }
            };
        }
    }
});