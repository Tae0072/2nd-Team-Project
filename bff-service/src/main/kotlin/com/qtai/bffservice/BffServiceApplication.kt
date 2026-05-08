package com.qtai.bffservice

import org.springframework.boot.autoconfigure.SpringBootApplication
import org.springframework.boot.runApplication

@SpringBootApplication
class BffServiceApplication

fun main(args: Array<String>) {
    runApplication<BffServiceApplication>(*args)
}