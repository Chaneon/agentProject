package com.agent.legal.mapper;

import com.agent.legal.model.entity.TaskReminder;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.time.LocalDateTime;
import java.util.List;

public interface TaskReminderMapper extends JpaRepository<TaskReminder, Integer> {
    /**
     * 根据接收人ID查询所有未完成的任务提醒
     * Spring Data JPA 根据方法名自动生成 SQL，等效于：
     * SELECT * FROM task_reminder WHERE assigned_to = ? AND is_completed = false
     *
     * @param userId 用户ID（assignee，任务分配给的用户）
     * @return 该用户所有未完成的任务列表
     *
     * 使用场景：用户登录首页时，展示待处理任务清单
     */
    List<TaskReminder> findByAssignedToAndIsCompletedFalse(Integer userId);
    /**
     * 查询所有截止日期早于指定时间且未完成的任务
     * 等效 SQL：SELECT * FROM task_reminder WHERE due_date < ? AND is_completed = false
     *
     * @param now 当前时间（通常传入 LocalDateTime.now()）
     * @return 所有已过期但未完成的任务列表
     *
     * 使用场景：定时任务每天凌晨扫描，筛选出过期的未完成任务，发送催办通知
     */
    List<TaskReminder> findByDueDateBeforeAndIsCompletedFalse(LocalDateTime now);

    /**
     * 将指定任务标记为已完成
     *
     * @Modifying 表示该查询会修改数据（执行 UPDATE/DELETE），需要事务支持
     * @Query 使用 JPQL（Java Persistence Query Language）编写自定义更新语句
     *        UPDATE TaskReminder t：TaskReminder 是实体类名，不是表名
     *        t.isCompleted = true：设置状态为已完成
     *        WHERE t.taskId = :taskId：条件：任务ID匹配
     *
     * @param taskId 任务ID
     *
     * 使用场景：用户点击任务列表中的“完成”按钮，将此任务标记为已处理
     *
     * 注意：
     * 1. 此方法需要在事务中执行（通常 Service 层加 @Transactional）
     * 2. 返回值可以是 int（影响行数）或 void
     * 3. 建议配合 @Modifying(clearAutomatically = true) 清除一级缓存，避免脏数据
     */
    @Modifying
    @Query("UPDATE TaskReminder t SET t.isCompleted = true WHERE t.taskId = :taskId")
    void markCompleted(@Param("taskId") Integer taskId);
}
