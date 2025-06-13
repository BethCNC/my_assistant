import React from 'react';
import Image from 'next/image';
import styles from './ChatInterface.module.css';

const ChatInterface = () => {
  return (
    <div className={styles.chatContainer}>
      <div className={styles.content}>
        {/* Header */}
        <div className={styles.header}>
          <div className={styles.iconNameDefault}>
            <div className={styles.navigationText}>
              <Image 
                className={styles.smileyIcon} 
                width={36} 
                height={36} 
                alt="Beth's Assistant" 
                src="/assets/smiley.svg" 
              />
            </div>
            <div className={styles.navigationText1}>
              <div className={styles.name}>Beth's Assistant</div>
            </div>
          </div>
          <div className={styles.dateTime}>
            <div className={styles.navigationText2}>
              <div className={styles.name}>Friday</div>
            </div>
            <div className={styles.navigationText2}>
              <div className={styles.name}>June 6, 2025</div>
            </div>
            <div className={styles.navigationText2}>
              <div className={styles.time}>11:25 AM</div>
            </div>
          </div>
        </div>

        <div className={styles.mainContainer}>
          {/* Sidebar */}
          <div className={styles.sidebar}>
            <div className={styles.recentChats}>
              <div className={styles.labelText}>
                <div className={styles.newChatButton}>Recent Chats</div>
              </div>
              <div className={styles.leadIcon}>
                <Image 
                  className={styles.arrowIcon} 
                  width={31} 
                  height={21} 
                  alt="Arrow" 
                  src="/assets/icon-arrow.svg" 
                />
              </div>
            </div>
            
            <div className={styles.leftColumn}>
              <div className={styles.recentChats1}>
                {Array.from({ length: 9 }, (_, i) => (
                  <div key={i} className={styles.chatHistory}>
                    <div className={styles.chatHistory1}>
                      <div className={styles.howCanI}>How can I better update my design tokens</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className={styles.newChatButton1}>
              <div className={styles.labelText}>
                <b className={styles.newChatButton2}>New Chat</b>
              </div>
              <div className={styles.icons}>
                <Image 
                  className={styles.plusIcon} 
                  width={32} 
                  height={32} 
                  alt="Plus" 
                  src="/assets/icon-plus.svg" 
                />
              </div>
            </div>
          </div>

          {/* Main Content */}
          <div className={styles.mainContainer1}>
            <div className={styles.contentContainer}>
              <div className={styles.container}>
                {/* Tool Buttons */}
                <div className={styles.buttonContainer}>
                  {['Notion', 'Figma', 'Github', 'Email', 'Calendar'].map((tool) => (
                    <div key={tool} className={styles.toolButton}>
                      <div className={styles.labelText2}>
                        <b className={styles.notion}>{tool}</b>
                      </div>
                    </div>
                  ))}
                </div>

                {/* Greeting */}
                <div className={styles.greeting}>
                  <div className={styles.greetingText}>
                    Good Morning Beth! What can I help you with today?
                  </div>
                </div>
              </div>

              {/* Suggestions */}
              <div className={styles.suggestionParent}>
                {Array.from({ length: 6 }, (_, i) => (
                  <div key={i} className={styles[`suggestion${i === 0 ? '' : i}`]}>
                    <div className={styles.shapeWrapper}>
                      <div className={styles.suggestionShapes}>
                        <Image 
                          className={styles.vectorIcon} 
                          width={32} 
                          height={32} 
                          alt="Shape" 
                          src="/assets/star.svg" 
                        />
                      </div>
                    </div>
                    <div className={styles.iWouldLike}>I would like to know about design tokens</div>
                    <div className={styles.icons}>
                      <Image 
                        className={styles.arrowIcon1} 
                        width={31} 
                        height={21} 
                        alt="Arrow" 
                        src="/assets/icon-arrow.svg" 
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Chat Input */}
            <div className={styles.chatInput}>
              <div className={styles.chatInputDefault}>
                <div className={styles.textarea}>
                  <div className={styles.input}>
                    <div className={styles.text}>Ask me a question...</div>
                  </div>
                </div>
              </div>
              <div className={styles.controls1}>
                <div className={styles.controlsLeft}>
                  <div className={styles.iconButtons}>
                    <div className={styles.icons6}>
                      <Image 
                        className={styles.filesIcon} 
                        width={22} 
                        height={24} 
                        alt="Files" 
                        src="/assets/icon-paperclip.svg" 
                      />
                    </div>
                  </div>
                  <div className={styles.iconButtons}>
                    <div className={styles.icons6}>
                      <Image 
                        className={styles.imagesIcon} 
                        width={24} 
                        height={20} 
                        alt="Images" 
                        src="/assets/icon-camera.svg" 
                      />
                    </div>
                  </div>
                </div>
                <div className={styles.controlsRight}>
                  <div className={styles.charCount}>0/1000</div>
                  <div className={styles.iconButtons}>
                    <div className={styles.icons6}>
                      <Image 
                        className={styles.sendIcon} 
                        width={24} 
                        height={22} 
                        alt="Send" 
                        src="/assets/icon-send.svg" 
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;