package com.agent.legal.mapper;

import com.agent.legal.model.entity.Contract;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface ContractMapper extends JpaRepository<Contract, Integer> {
    //根据创建人查询
    List<Contract> findByCreatedBy(Integer userId);
}
