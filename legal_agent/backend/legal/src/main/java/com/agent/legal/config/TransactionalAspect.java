package com.agent.legal.config;

import org.aspectj.lang.ProceedingJoinPoint;
import org.aspectj.lang.annotation.Around;
import org.aspectj.lang.annotation.Aspect;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.jdbc.datasource.DataSourceTransactionManager;
import org.springframework.stereotype.Component;
import org.springframework.transaction.TransactionDefinition;
import org.springframework.transaction.TransactionStatus;
import org.springframework.transaction.support.DefaultTransactionDefinition;

@Aspect
@Component
public class TransactionalAspect {

    @Autowired
    private DataSourceTransactionManager transactionManager;

    @Around("execution(public * com.agent.legal.service.*.*(..))")
    public Object manageTransaction(ProceedingJoinPoint joinPoint) throws Throwable {
        DefaultTransactionDefinition def = new DefaultTransactionDefinition();
        // 1. 创建事务定义，设置传播行为为 REQUIRED
        def.setPropagationBehavior(TransactionDefinition.PROPAGATION_REQUIRED);
        // 2. 获取事务状态（开启事务）
        TransactionStatus status = transactionManager.getTransaction(def);
        try {
            // 3. 执行目标方法（业务逻辑）
            Object result = joinPoint.proceed();
            // 4. 方法执行成功，提交事务
            transactionManager.commit(status);
            return result;
        } catch (Throwable ex) {
            // 5. 方法抛出异常，回滚事务
            transactionManager.rollback(status);
            // 继续向上抛出异常，让上层感知
            throw ex;
        }
    }
}
